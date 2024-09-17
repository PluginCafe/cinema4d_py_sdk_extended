"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam, Ferdinand Hoppe

Highlights the key-functionalities of maxon.DataDictionary.

Topics:
    - Constructing DataDictionary instances.
    - Reading, writing, and deleting key-value pairs.
    - Retrieving the number of contained pairs.
    - Testing if a specific key is contained.
    - Testing equality.
"""
import typing
import maxon

def main():
    # A Python dictionary object as a data source.
    pyDict: dict = {42: "The answer.", "pi": 3.1415, True: "A string"}

    # Create a reference to a `DataDictionaryInterface` object.
    dataDict: maxon.DataDictionary = maxon.DataDictionary()

    # Items can be set with the `.Set` method or with the bracket syntax. Just as the standard 
    # Python dictionary, the type `DataDictionary` supports mixed key and value types.
    dataDict.Set("myKey", "foo")
    for key, value in pyDict.items():
        dataDict[key] = value

    # However, only the most atomic Python types as string, int, float, and bool are being
    # automatically converted to their Maxon API equivalent. For storing a list of integer values 
    # under a key for example, one must convert that list explicitly to a BaseArray.
    dataDict["prime_numbers"] = maxon.BaseArray(maxon.Int32, [2, 3, 5, 7, 11, 13])
    
    # The number of key-value pairs in a `DataDictionary` instance can be evaluated with with 
    # `len()` and `.GetCount()`. Alternatively, `.IsPopulated()` or `IsEmpty() can be called to 
    # evaluate if an instance is empty or not.
    length: int = len(dataDict)
    alsoLength: int = dataDict.GetCount()
    isPopulated: bool = dataDict.IsPopulated()
    isEmpty: bool = dataDict.IsEmpty()
    print (f"\ndataDict: {length = }, {alsoLength = },  {isPopulated = },  {isEmpty = }")

    # Other than the standard Python dictionary, a `DataDictionary` instance will yield directly 
    # key-value pairs when iterated. Values can also be accessed with the bracket syntax and the
    # method `.Get` which works similar to the method of the same name of a Python dict.
    print ("\nState of dataDict:")
    for key, value in dataDict:
        print (f"\t{key = }, {value = }")

    pi: float = dataDict["pi"]
    # Will return the default value None, as the key "bar" does not exist.
    bar: typing.Optional[str] = dataDict.Get("bar", None)

    # The occurrence of a key can be tested with the keyword `in` or the method `.Contains()`.
    hasKeyPi: bool = "pi" in dataDict
    hasKeyBar: bool = dataDict.Contains("bar")
    print (f"\ndataDict: {hasKeyPi = }, {hasKeyBar = }")

    # Key-value pairs can be removed with the `del` keyword or the method `.Erase()`.
    del dataDict["pi"]
    dataDict.Erase(42)
    
    print ("\nNew state of dataDict:")
    for key, value in dataDict:
        print (f"\t{key = }, {value = }")

    # DataDictionary instances can also be compared for equaltiy but the comparison is carried out
    # as an identity comparison.

    # Two data dictionaries which are are being filled with the same content.
    aData: maxon.DataDictionary = maxon.DataDictionary()
    bData: maxon.DataDictionary = maxon.DataDictionary()

    aData[1000] = "Hello World!"
    aData["value"] = 42
    bData[1000] = "Hello World!"
    bData["value"] = 42

     # Will evaluate as `True` because `xData` points to the same object as `aData`.
    xData: maxon.DataDictionary = aData
    print (f"\n{aData == xData = }")

    # Will evaluate as `False` because `aData` points to another object than `bData`. Not the
    # content is being compared, but the identity of the two objects.
    print (f"{aData == bData = }")

if __name__ == "__main__":
    main()