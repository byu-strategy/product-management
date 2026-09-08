# Product

The build itself: code, config, whatever runs.

If you build an AI feature, put its eval set in `evals/`. An eval is a set of real inputs
plus what a good output looks like for each, scored so you can tell whether a change to a
prompt or a model actually helped. Twenty examples in a JSON file and a script that loops
over them is enough to catch a regression.
