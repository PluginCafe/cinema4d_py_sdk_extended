"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Iterates over the content of a BaseContainer.

Class/method highlighted:
    - c4d.BaseContainer

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object")

    # Retrieves the data stored into the BaseContainer of the object
    bc = op.GetData()
    if bc is None:
        raise RuntimeError("Failed to retrieve bc")

    # Iterates over the content of the BaseContainer using a for loop
    for key in range(len(bc)):
        # Check if the data retrieved can be printed in python (some DataType are not supported in Python)
        key = bc.GetIndexId(key)
        try:
            print(key, bc[key])
        except AttributeError:
            print("Entry:{0} is DataType {1} and can't be printed in Python".format(key, bc.GetType(key)))


if __name__ == "__main__":
    main()
