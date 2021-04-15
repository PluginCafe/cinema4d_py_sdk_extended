"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Searches for the BaseOverride of the given material and its color parameter.
    - If found, the color value is applied to the backup value and transfers the state of this Take to the backup Take.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.GetCurrentTake()
    - BaseTake.FindOverrideCounterPart()
    - BaseOverride.UpdateSceneNode()

"""
import c4d


def main():
    # Gets the selected Material from the active document
    material = doc.GetActiveMaterial()
    if material is None:
        raise RuntimeError("Failed to retrieve the selected material.")

    # Gets the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Gets the active take and check it's not the main one
    take = takeData.GetCurrentTake()
    if take.IsMain():
        raise RuntimeError("The selected take is already the main one.")

    # Checks if there is an override in this Take from the selected material
    baseOverride = take.FindOverride(takeData, material)
    if baseOverride is None:
        raise RuntimeError("Failed to find the base override.")

    # Gets the DescID corresponding to the diffuse color of a material
    ID = c4d.DescID(c4d.DescLevel(c4d.MATERIAL_COLOR_COLOR, c4d.DTYPE_COLOR, 0))

    # Finds the backup node for this override (aka default parameter)
    backup, result = takeData.FindOverrideCounterPart(baseOverride, ID)
    if not backup:
        raise RuntimeError("Failed to find the default override.")

    # Retrieves the value stored in the override (the changed value)
    data = baseOverride.GetParameter(ID, c4d.DESCFLAGS_GET_0)

    # Sets the default value to the value stored in the override
    backup.SetParameter(ID, data, c4d.DESCFLAGS_SET_0)

    # Updates the scene with the new Take
    backup.UpdateSceneNode(takeData, ID)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
