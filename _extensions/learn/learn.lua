--[[
learn.lua: turn each `<!-- learn -->` comment into a "Learn this section with Claude" callout.

The callout holds one copyable line, `/learn <page url>#<anchor>`, which the student pastes into
Claude Code to run the builder-template /learn skill on that section.

The anchor is the identifier pandoc already gave the enclosing `##` heading, so it is always the
real id on the page: nothing is recomputed and nothing is typed by hand. The page URL is the site
URL plus this file's name with .html. Set `learn-base-url` in _quarto.yml to change the site.

A marker before any `##` heading, or under a `#` heading only, is dropped with a warning.
]]

local DEFAULT_BASE = "https://byu-strategy.github.io/product-management/"

local function is_marker(block)
  return block.t == "RawBlock"
    and (block.format == "html" or block.format == "markdown")
    and block.text:match("^%s*<!%-%-%s*learn%s*%-%->%s*$") ~= nil
end

local function page_name()
  local input = quarto.doc.input_file or ""
  local name = input:match("([^/\\]+)%.[^.]+$") or input
  return name .. ".html"
end

local function callout(url)
  local line = "/learn " .. url
  return quarto.Callout({
    type = "tip",
    title = "Learn this section with Claude",
    content = pandoc.Blocks({
      pandoc.Para({ pandoc.Str("Paste this into Claude Code to learn this section from first principles, on your own product, as quick or as deep as you have time for.") }),
      pandoc.CodeBlock(line, pandoc.Attr("", { "default", "learn-command" })),
    }),
  })
end

function Pandoc(doc)
  local base = DEFAULT_BASE
  if doc.meta["learn-base-url"] then
    base = pandoc.utils.stringify(doc.meta["learn-base-url"])
    if not base:match("/$") then base = base .. "/" end
  end
  local page = base .. page_name()

  local section = nil
  local out = pandoc.Blocks({})
  local found = 0
  for _, block in ipairs(doc.blocks) do
    if block.t == "Header" and block.level <= 2 then
      section = (block.level == 2) and block.identifier or nil
    end
    if is_marker(block) then
      if section and section ~= "" then
        out:insert((callout(page .. "#" .. section)))  -- parentheses: quarto.Callout returns more than one value
        found = found + 1
      else
        quarto.log.warning("learn: a <!-- learn --> marker in " .. page_name() .. " has no ## heading above it; skipped")
      end
    else
      out:insert(block)
    end
  end
  doc.blocks = out
  return doc
end
