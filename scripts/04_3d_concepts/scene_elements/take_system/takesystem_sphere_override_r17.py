"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Checks if the given Take contains an override for the given sphere object.
    - If so, it is checked if the "Radius" parameter is overridden, in this case, the value is increased and the node updated.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.GetCurrentTake()
    - BaseTake.FindOverride()
    - BaseOverride.IsOverriddenParam()

Compatible:
    - Win / Mac
    - R17, R18, R19, R20, R21, S22
"""
import c4d


def main():
    # Checks if there is an active object and if it's a Sphere object
    if op is None:
        raise ValueError("op is none, please select one object.")

    if not op.CheckType(c4d.Osphere):
        raise TypeError("The objects is not a sphere.")

    # Gets the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Gets the active Take and check it's not the main one
    take = takeData.GetCurrentTake()
    if take is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Checks if there is an override in this Take from the selected sphere object
    baseOverride = take.FindOverride(takeData, op)
    if baseOverride is None:
        raise RuntimeError("Failed to find the base override.")

    # Gets the DescID corresponding to the sphere radius and leave if this parameter is not already overridden
    ID = c4d.DescID(c4d.DescLevel(c4d.PRIM_SPHERE_RAD, c4d.DTYPE_REAL, 0))
    if not baseOverride.IsOverriddenParam(ID):
        raise RuntimeError("The parameter is already overridden.")

    # Retrieves the current values stored in the Take
    data = baseOverride.GetParameter(ID, c4d.DESCFLAGS_GET_0)

    # Add 10 to the values
    data = data + 10.0

    # Pushes back the modified value to the override
    baseOverride.SetParameter(ID, data, c4d.DESCFLAGS_SET_0)

    # Updates the scene with the new Take
    baseOverride.UpdateSceneNode(takeData, ID)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
