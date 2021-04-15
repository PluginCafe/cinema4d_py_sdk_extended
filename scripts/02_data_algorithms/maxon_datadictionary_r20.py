"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Converts a Python dictionary to a Maxon Data Dictionary.

Class/method highlighted:
    - maxon.DataDictionary
    - DataDictionary.Set()

"""
import maxon


def main():
    # Creates a python dictionary object
    pyDict = {'foo': 1, 'something': 20.05, 'test': 'A string'}

    # Creates a maxon data dictionary object
    mDict = maxon.DataDictionary()

    # Sets the value of the tuple
    for key, value in pyDict.items():
        mDict.Set(key, value)

    print(mDict)


if __name__ == "__main__":
    main()