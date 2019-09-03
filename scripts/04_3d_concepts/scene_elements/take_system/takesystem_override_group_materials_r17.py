"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Creates a Take with an override group for each selected material.
    - Adds the object "object" to the newly created group.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.AddTake()
    - BaseTake.AddOverrideGroup()
    - BaseOverrideGroup.AddToGroup()
    - BaseOverrideGroup.AddTag()

Compatible:
    - Win / Mac
    - R17, R18, R19, R20, R21
"""
import c4d


def main():
    # Checks if there is an active object
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Retrieves selected materials
    materials = doc.GetActiveMaterials()
    if materials is None:
        raise RuntimeError("There is no active materials.")

    # Gets the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Loops over all selected materials
    for material in materials:

        # Creates a Take for each material
        take = takeData.AddTake(material.GetName(), None, None)
        if take is None:
            continue

        # Creates an override group for this Take
        group = take.AddOverrideGroup()
        if group is None:
            continue

        # Adds this group to the global TakeData
        group.AddToGroup(takeData, op)

        # Adds a texture tag to the override (aka this Take will create a tag)
        tag = group.AddTag(takeData, c4d.Ttexture, material)
        if tag is None:
            continue

        # Defines how the projection will ne done
        tag[c4d.TEXTURETAG_PROJECTION] = c4d.TEXTURETAG_PROJECTION_UVW

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()