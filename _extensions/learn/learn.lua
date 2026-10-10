--[[
learn.lua: give each section that ends with a `<!-- learn -->` comment a small "Learn" button
beside its `##` heading.

The button copies one line, `/learn <page url>#<anchor>`, which the student pastes into Claude
Code to run the builder-template /learn skill on that section. learn.js draws the button and does
the copying; this filter only marks the heading with `data-learn`, so the table of contents and the
heading text are untouched.

The anchor is the identifier pandoc already gave the `##` heading, so it is always the real id on
the page. The page URL is the site URL plus this file's name with .html. Set `learn-base-url` in
_quarto.yml to change the site. A marker before any `##` heading is dropped with a warning.
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

function Pandoc(doc)
  local base = DEFAULT_BASE
  if doc.meta["learn-base-url"] then
    base = pandoc.utils.stringify(doc.meta["learn-base-url"])
    if not base:match("/$") then base = base .. "/" end
  end
  local page = base .. page_name()

  -- pass 1: which ## sections end with a marker
  local marked, section = {}, nil
  for _, block in ipairs(doc.blocks) do
    if block.t == "Header" and block.level <= 2 then
      section = (block.level == 2) and block.identifier or nil
    elseif is_marker(block) then
      if section and section ~= "" then
        marked[section] = true
      else
        quarto.log.warning("learn: a <!-- learn --> marker in " .. page_name() .. " has no ## heading above it; skipped")
      end
    end
  end

  -- pass 2: drop the markers and tag the marked headings
  local out, found = pandoc.Blocks({}), 0
  for _, block in ipairs(doc.blocks) do
    if is_marker(block) then
      -- dropped
    else
      if block.t == "Header" and block.level == 2 and marked[block.identifier] then
        block.attributes["data-learn"] = "/learn " .. page .. "#" .. block.identifier
        found = found + 1
      end
      out:insert(block)
    end
  end
  doc.blocks = out

  if found > 0 then
    quarto.doc.add_html_dependency({
      name = "learn-button",
      version = "2.0.0",
      scripts = { "learn.js" },
      stylesheets = { "learn.css" },
    })
  end
  return doc
end
