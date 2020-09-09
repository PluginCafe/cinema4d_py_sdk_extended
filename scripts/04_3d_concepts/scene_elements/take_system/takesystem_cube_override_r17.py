"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Adds an override to the current Take for the object (that must be a cube) and changes the "Size" parameter.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.GetCurrentTake()
    - BaseTake.FindOverrideCounterPart()
    - BaseOverride.UpdateSceneNode()

Compatible:
    - Win / Mac
    - R17, R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Checks if there is an active object and if it's a Cube object
    if op is None:
        raise ValueError("op is none, please select one object.")

    if not op.CheckType(c4d.Ocube):
        raise TypeError("The objects is not a cube.")

    # Gets the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Gets the active Take and check it's not the main one
    take = takeData.GetCurrentTake()
    if take.IsMain():
        raise RuntimeError("The selected take is already the main one.")

    # Gets the DescID corresponding to the Cube size
    ID = c4d.DescID(c4d.DescLevel(c4d.PRIM_CUBE_LEN, c4d.DTYPE_VECTOR, 0), c4d.DescLevel(c4d.VECTOR_X, c4d.DTYPE_REAL, 0))
    newValue = 300.0

    # Add an override if this parameter is not already overridden, otherwise returns the already existing override
    overrideNode = take.FindOrAddOverrideParam(takeData, op, ID, newValue)
    if overrideNode is None:
        raise RuntimeError("Failed to find the override node.")

    # Updates the scene with the new Take
    overrideNode.UpdateSceneNode(takeData, ID)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
