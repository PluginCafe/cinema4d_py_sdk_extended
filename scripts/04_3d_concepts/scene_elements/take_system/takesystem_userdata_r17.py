"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Adds a new boolean userdata parameter to the given BaseTake.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.GetCurrentTake()

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

    # Gets the active Take and check it's not the main one
    take = takeData.GetCurrentTake()
    if take.IsMain():
        raise RuntimeError("The selected take is already the main one.")

    # Creates a Custom Bool Datatype
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_BOOL)
    if bc is None:
        raise RuntimeError("Failed to create a BaseContainer.")
    bc[c4d.DESC_NAME] = "Enable"

    # Adds an User Data to the Take
    userData = take.AddUserData(bc)

    # Sets the value to True
    take.SetParameter(userData, True, c4d.DESCFLAGS_SET_0)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
