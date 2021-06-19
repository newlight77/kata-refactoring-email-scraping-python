"""[summary]
convert a dict to an object
"""

# pylint: disable=too-few-public-methods
class DefDictToObject():
    def __init__(self, myDict):
        for key, value in myDict.items():
            if type(value) == dict:
                setattr(self, key, DefDictToObject(value))
            else:
                setattr(self, key, value)
