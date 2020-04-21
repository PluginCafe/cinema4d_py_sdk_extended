"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Basic usage of a BaseContainer.

Class/method highlighted:
    - c4d.BaseContainer

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22
"""
import c4d


def main():
    # Creates a BaseContainer
    bc = c4d.BaseContainer()

    aString = "Something"
    # Defines the value of the entry index 0, data are copied
    bc[0] = aString

    # Changes the value of the variable (this will not affect the content of the BaseContainer
    aString = "Something Else"

    # Retrieves the value stored in the BaseContainer
    print(bc.GetString(0, "Default Value"), aString)


if __name__ == "__main__":
    main()
