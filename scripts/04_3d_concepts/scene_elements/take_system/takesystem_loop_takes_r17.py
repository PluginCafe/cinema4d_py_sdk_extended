"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Loops through all Takes that are direct child Takes of the main Take.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.GetMainTake()
    - GeListNode.GetDown()
    - GeListNode.GetNext()

Compatible:
    - Win / Mac
    - R17, R18, R19, R20, R21, S22
"""
import c4d


def main():
    # Gets the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Gets the main Take, aka the first one
    mainTake = takeData.GetMainTake()

    # Get the child of this one
    take = mainTake.GetDown()

    # Loops through all Takes
    while take:
        print("Take Name: {0}.".format(take.GetName()))

        # Get the next Takes
        take = take.GetNext()


if __name__ == '__main__':
    main()
