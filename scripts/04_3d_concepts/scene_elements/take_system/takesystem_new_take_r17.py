"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Creates a new Take and makes it the current one.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.AddTake()
    - TakeData.SetCurrentTake()

Compatible:
    - Win / Mac
    - R17, R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Gets the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Adds a new Take
    newTake = takeData.AddTake("this is a new take", None, None)
    if newTake is None:
        raise RuntimeError("Failed to add a new take.")

    # Defines the created Take as the active one
    takeData.SetCurrentTake(newTake)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
