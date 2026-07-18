/**
 * Shared helpers for the concurrent-agent coordination hooks (bash-guard).
 * Ported from sdmurff/agent-team-kit, trimmed for this Quarto repo (no
 * dev-port or schema-lock hooks here).
 *
 * All cross-session state lives under a single directory anchored to the
 * COMMON git dir, so every git worktree AND the main checkout resolve to the
 * SAME absolute path. It sits inside `.git`, so it is never tracked.
 */
import { readFileSync, mkdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join } from "node:path";

export function payload() {
  let raw = "";
  try {
    raw = readFileSync(0, "utf8");
  } catch {
    /* no stdin */
  }
  try {
    return JSON.parse(raw || "{}");
  } catch {
    return {};
  }
}

export function coordDir(cwd) {
  const base = cwd || process.cwd();
  let gitDir;
  try {
    gitDir = execFileSync("git", ["rev-parse", "--git-common-dir"], {
      cwd: base,
      encoding: "utf8",
    }).trim();
  } catch {
    gitDir = join(base, ".git");
  }
  const abs = gitDir.startsWith("/") ? gitDir : join(base, gitDir);
  const dir = join(abs, ".wg-agent");
  try {
    mkdirSync(dir, { recursive: true });
  } catch {
    /* already there */
  }
  return dir;
}

// True when cwd is inside a LINKED git worktree (not the main checkout): a
// linked worktree's per-tree git dir differs from the shared common dir. Used
// to auto-relax the shared-working-tree git guards in worktree mode, where each
// agent has its own isolated tree and blanket/destructive git is safe again.
export function isLinkedWorktree(cwd) {
  const base = cwd || process.cwd();
  try {
    const out = execFileSync(
      "git",
      ["rev-parse", "--git-dir", "--git-common-dir"],
      { cwd: base, encoding: "utf8" },
    )
      .trim()
      .split("\n");
    return out.length >= 2 && out[0] !== out[1];
  } catch {
    return false;
  }
}

// Drop quoted substrings so a commit message like `-m "ran git add ."` can't
// trip the command guards.
export function unquote(cmd) {
  return cmd.replace(/"[^"]*"/g, '""').replace(/'[^']*'/g, "''");
}
