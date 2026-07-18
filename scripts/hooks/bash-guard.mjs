#!/usr/bin/env node
/**
 * PreToolUse (Bash), git-safety guard for many-agents-on-one-`main`.
 * Ported from sdmurff/agent-team-kit, trimmed for this Quarto repo: the
 * schema-lock and psql-DDL guards were dropped (no database here).
 *
 *  A. Git safety, block tree-wide staging / destructive commands that would
 *     sweep in OR destroy other agents' uncommitted work in the shared tree.
 *  B. Anti-sweep, block a pathspec-less commit that would carry files this
 *     session never staged (the shared-index sweep).
 *
 * Exit 2 + stderr blocks the command and tells Claude why; exit 0 allows.
 */
import { readFileSync, appendFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join } from "node:path";
import { payload, coordDir, unquote, isLinkedWorktree } from "./agent-coord.mjs";

// --- A. git-safety patterns (block on match). Flags must sit right after the
// subcommand, so quoted/parenthetical mentions don't false-trip.
// `sharedTreeOnly` blocks exist solely to protect a SHARED working tree; they
// auto-relax inside a linked worktree (worktree mode), where each agent's tree
// is its own. Force-push has no such flag, it's dangerous from anywhere. ---
const GIT_BLOCKS = [
  {
    sharedTreeOnly: true,
    re: /\bgit\s+add\s+(-A\b|--all\b|\.(?:\s|$))/,
    msg: "Blanket `git add` stages the WHOLE working tree, on shared `main` that sweeps in other agents' in-flight changes (and this tree collects stray OneDrive files). Stage explicit paths: `git add <file> <file>`.",
  },
  {
    sharedTreeOnly: true,
    re: /\bgit\s+commit\s+-[a-zA-Z]*a[a-zA-Z]*\b/,
    msg: "`git commit -a/-am` stages every modified tracked file, including other agents' work. Stage your explicit paths first, then `git commit -m`.",
  },
  {
    sharedTreeOnly: true,
    re: /\bgit\s+reset\s+--hard\b/,
    msg: "`git reset --hard` discards the ENTIRE working tree, it would destroy other agents' uncommitted work. Revert only your own paths (`git checkout -- <file>`), or ask the human.",
  },
  {
    sharedTreeOnly: true,
    re: /\bgit\s+clean\s+-[a-zA-Z]*f/,
    msg: "`git clean -f` deletes untracked files across the whole tree, including other agents' new files. Don't run it on shared `main`.",
  },
  {
    sharedTreeOnly: true,
    re: /\bgit\s+stash\b(?!\s+(list|show|pop|apply|drop))/,
    msg: "`git stash` pockets EVERY agent's uncommitted changes, not just yours. Don't stash on shared `main`.",
  },
  {
    sharedTreeOnly: true,
    re: /\bgit\s+checkout\s+(?:--\s+)?\.(?:\s|$)/,
    msg: "`git checkout -- .` reverts the whole tree, destroying other agents' uncommitted work. Revert only your own explicit paths.",
  },
  {
    re: /\bgit\s+push\b[^|&;]*(--force\b|--force-with-lease\b|\s-f\b)/,
    msg: "Force-push rewrites published history. Never force-push `main`. (Normal pushes go through the `/push` skill, run by the human.)",
  },
];

// --- B. anti-sweep (shared index) ---------------------------------------------
// The git index is SHARED across every agent on this `.git`, so a pathspec-less
// `git commit` commits the WHOLE index, including files another agent staged a
// moment ago. We record the paths THIS session stages (git add/mv/rm) and block
// a pathspec-less commit that would carry files this session never staged. The
// fix it points to is the right pattern anyway:
// `git commit -m "..." -- <your paths>` commits only those.
function ownedLedger(p) {
  return join(coordDir(p.cwd), `staged-${p.session_id || "x"}.txt`);
}

function recordStaged(cmd, p) {
  const paths = [];
  for (const m of cmd.matchAll(/\bgit\s+(?:add|mv|rm|stage)\b([^|&;]*)/g)) {
    for (const a of m[1].split(/\s+/))
      if (a && !a.startsWith("-") && a !== "--") paths.push(a);
  }
  if (!paths.length) return;
  try {
    appendFileSync(ownedLedger(p), paths.join("\n") + "\n");
  } catch {
    /* best-effort ledger */
  }
}

function commitSweepBlock(cmd, p) {
  if (!/\bgit\s+commit\b/.test(cmd)) return null;
  if (/--amend\b/.test(cmd)) return null; // amend is a separate (message) flow
  if (/\s--(\s|$)/.test(cmd)) return null; // explicit `-- <pathspec>`, already scoped
  let staged;
  try {
    staged = execFileSync("git", ["diff", "--cached", "--name-only"], {
      cwd: p.cwd,
      encoding: "utf8",
    })
      .split("\n")
      .filter(Boolean);
  } catch {
    return null; // not a repo / git error, don't block
  }
  if (!staged.length) return null;
  let owned = new Set();
  try {
    owned = new Set(
      readFileSync(ownedLedger(p), "utf8").split("\n").filter(Boolean),
    );
  } catch {
    /* no ledger, nothing owned yet */
  }
  const foreign = staged.filter((f) => !owned.has(f));
  if (!foreign.length) return null; // everything staged is ours, safe
  return (
    `This pathspec-less \`git commit\` would sweep ${foreign.length} file(s) you didn't stage ` +
    `into your commit, another agent staged them in the shared index:\n  ` +
    foreign.slice(0, 8).join("\n  ") +
    (foreign.length > 8 ? `\n  ...+${foreign.length - 8} more` : "") +
    `\nCommit only your own paths: \`git commit -m "..." -- <your files>\` ` +
    `(commits just those, ignoring the rest of the shared index).`
  );
}

function main() {
  const p = payload();
  if ((p.tool_name || "") !== "Bash") process.exit(0);
  const raw = p.tool_input?.command || "";
  if (!raw) process.exit(0);
  const cmd = unquote(raw);

  // In a linked worktree each agent's tree is its own, so the shared-tree git
  // blocks (blanket-stage, reset --hard, clean, stash, checkout -- .) are safe
  // and auto-relax. Force-push (no sharedTreeOnly flag) stays blocked anywhere.
  const linked = isLinkedWorktree(p.cwd);
  for (const g of GIT_BLOCKS) {
    if (linked && g.sharedTreeOnly) continue;
    if (g.re.test(cmd)) {
      process.stderr.write(g.msg + "\n");
      process.exit(2);
    }
  }

  // Anti-sweep is a shared-tree concern; a linked worktree has its own index.
  if (!linked) {
    recordStaged(cmd, p);
    const sweepMsg = commitSweepBlock(cmd, p);
    if (sweepMsg) {
      process.stderr.write(sweepMsg + "\n");
      process.exit(2);
    }
  }

  process.exit(0);
}

main();
