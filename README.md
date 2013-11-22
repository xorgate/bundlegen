bundlegen
=========

script to generate ios settings bundles from json without hurting your brain

Syntax:

$ python bundlegen.py sourcedir rootfilename destdir

eg.

$ python bundlegen.py ~/code/bundlejsons/ Root ~/projects/awesomeapp/Settings.bundle/

Will generate 2 plists. The Root.json specifies a child pane.


Example format can be found in Root.json and SubPage1.json
