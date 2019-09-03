"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Adds a new Take and creates a new override group for all selected objects.
    - If a material with the name "Green" exists a texture tag referencing that material is added to the override group.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.AddTake()
    - BaseTake.AddOverrideGroup()
    - BaseOverrideGroup.AddToGroup()

Compatible:
    - Win / Mac
    - R17, R18, R19, R20, R21
"""
import c4d


def main():
    # Retrieves selected objects
    objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    if not objects:
        raise RuntimeError("There is no objects selected.")

    # Gets the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Creates a Take
    take = takeData.AddTake("Green Objects", None, None)
    if take is None:
        raise RuntimeError("Failed to add a take.")

    # Adds an override Group
    group = take.AddOverrideGroup()
    if group is None:
        raise RuntimeError("Failed to create override group.")

    group.SetName("Green Material")

    # Searches for a material called "Green" in the active document, if found add a texture tag in this Take
    mat = doc.SearchMaterial("Green")
    if mat:
        group.AddTag(takeData, c4d.Ttexture, mat)

    # Loops through all selected objects and add them to the group
    for element in objects:
        group.AddToGroup(takeData, element)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()