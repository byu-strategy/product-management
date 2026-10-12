--[[
week-view.lua: hand the 14-week reading order to week-view.js, which adds a Topics | Weeks
switch to the left rail.

The weeks live in _weeks.yml under `week-view`, loaded into every page by `metadata-files` in
_quarto.yml. This filter writes them into the page as JSON and attaches the script and styles.
Which week is "This week" is decided in the reader's browser from today's date, so the site
never needs a rebuild to move forward.
]]

local function plain(v)
  local t = pandoc.utils.type(v)
  if t == "List" then
    local out = {}
    for i, x in ipairs(v) do out[i] = plain(x) end
    return out
  elseif t == "table" or t == "Meta" then
    local out = {}
    for k, x in pairs(v) do out[k] = plain(x) end
    return out
  elseif t == "boolean" or t == "number" then
    return v
  end
  return pandoc.utils.stringify(v)
end

function Meta(meta)
  if not quarto.doc.is_format("html") or not meta["week-view"] then return nil end
  local data = plain(meta["week-view"])
  local json = quarto.json.encode(data):gsub("</", "<\\/")
  quarto.doc.include_text("in-header", "<script>window.PM_WEEK_VIEW = " .. json .. ";</script>")
  quarto.doc.add_html_dependency({
    name = "week-view",
    version = "1.0.0",
    scripts = { "week-view.js" },
    stylesheets = { "week-view.css" },
  })
  return nil
end
