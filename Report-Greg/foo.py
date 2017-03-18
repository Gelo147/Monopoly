from json import loads, dumps

python_dict = {"command":"COMMAND",
               "valies": {
                   "value1":1,
                   "value2": 2,
               },
              }
# Turn the python dictionary into
# JavaScript Object Notation
x = dumps(python_dict)

# Turn the JavaScript Object Notation
# into python dictionary
new = loads(dict_in_jsObjectNotation)
