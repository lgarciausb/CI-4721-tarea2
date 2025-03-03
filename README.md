# Operator grammar parser generator

To make debugging easier a few extra commands were implemented

* SHOW

  displays the current state of the defined operator grammar

* RESET

  resets all provided parser settings

* SAVE [\<filename>]

  saves the state of the operator grammar into <filename>.json, if <filename> argument is not provided it is saved by default in parser.json

* LOAD [\<filename>]

  loads the state of the operator grammar from <filename>.json, if <filename> argument is not provided it is loaded by default from parser.json
