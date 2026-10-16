--[[
concepts.lua: passages in the book tagged with the builder concept they teach.

A passage is a fenced div with the class `concept` and the concept ids in `data-c`:

  ::: {.concept data-c="DE02"}
  ...the paragraphs, table, figure, and Try it that teach it...
  :::

One passage can teach several concepts (`data-c="DE07 DE08"`), and one concept can have several
passages. A div may hold `####` subheadings but never a `##` heading, so sections stay intact.

The ids come from scripts/grading/concepts/*.json, the concept list that the sprint reports,
the exam and /learn share. An id not on that list is a warning at render time. The filter adds
each concept's name as `data-cn` so concepts.js can label the passage, and loads concepts.js only
on pages with a tagged passage. concepts.js reads `?c=DE02` from the address, which is how a
sprint report links to a passage, and highlights every passage for that concept.
`scripts/grading/builder_concepts.py --passages` writes the map the reports read.
]]

local DIR = "scripts/grading/concepts"
local names = nil

local function load_names()
  if names then return names end
  names = {}
  local ok, files = pcall(pandoc.system.list_directory, DIR)
  if not ok then
    quarto.log.warning("concepts: " .. DIR .. " not found; concept ids are not checked")
    return names
  end
  for _, f in ipairs(files) do
    if f:match("%.json$") then
      local h = io.open(DIR .. "/" .. f, "r")
      if h then
        local good, d = pcall(pandoc.json.decode, h:read("a"), false)
        h:close()
        if good and type(d) == "table" then
          for _, c in ipairs(d.concepts or {}) do names[c.id] = c.name end
        end
      end
    end
  end
  return names
end

local found = false

function Div(div)
  if not div.classes:includes("concept") then return nil end
  local ids = div.attributes["c"] or div.attributes["data-c"] or ""
  local N, labels = load_names(), {}
  for id in ids:gmatch("%S+") do
    if next(N) ~= nil and not N[id] then
      quarto.log.warning("concepts: unknown concept id " .. id .. " in " .. (quarto.doc.input_file or "?"))
    end
    table.insert(labels, id .. " " .. (N[id] or ""))
  end
  div.attributes["cn"] = table.concat(labels, " | ")
  found = true
  return div
end

function Pandoc(doc)
  if found then
    quarto.doc.add_html_dependency({
      name = "concept-passages",
      version = "1.0.0",
      scripts = { "concepts.js" },
      stylesheets = { "concepts.css" },
    })
  end
  return doc
end
