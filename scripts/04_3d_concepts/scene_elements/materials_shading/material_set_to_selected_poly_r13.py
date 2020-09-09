"""
Copyright: MAXON Computer GmbH
Author: Manuel MAGALHAES

Description:
    - Apply the selected material to selected polygons on the selected object.

Class/method highlighted:
    - SelectionTag.GetBaseSelect()
    - BaseObject.MakeTag()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23
"""
import c4d


def AssignMatToObject(obj, matList, onlyToSelection=False):
    """
    Checks if the passed parameter are ok.
    :param obj: The BaseObject to apply the material.
    :type obj: Union[c4d.BaseObject, c4d.PolygonObject]
    :param matList: the materials list that must be applied.
    :type matList: list
    :param onlyToSelection: **True** to define if the material should be applied to only the selected polygons.
    :type onlyToSelection: bool
    """
    if obj is None:
        return False

    if matList is None or len(matList) == 0:
        return False

    # Loops trough the material list
    for mat in matList:
        # Creates the texture Tag
        textureTag = obj.MakeTag(c4d.Ttexture)
        doc.AddUndo(c4d.UNDOTYPE_NEW, textureTag)

        # If the texture tag is not available at this point, something went wrong
        if textureTag is None:
            raise RuntimeError("Failed to retrieve the texture tag.")

        # Sets the name of the texture tag with the name of the texture
        textureName = mat.GetName()
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, textureTag)
        textureTag[c4d.ID_BASELIST_NAME] = textureName

        # Assigns the material to the material tag
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, textureTag)
        textureTag[c4d.TEXTURETAG_MATERIAL] = mat

        # If we should not only apply to the selected polygon
        if not onlyToSelection:
            return True

        # Checks if the object is not a polygon object
        if not obj.CheckType(c4d.Opolygon):
            return True

        # Retrieves the selected polygon on the object
        selection = obj.GetPolygonS()

        # If the selection is not valid or empty we don't create the selection tag
        if selection is None or selection.GetCount() == 0:
            return True

        # Creates the selection tag
        selectionTag = obj.MakeTag(c4d.Tpolygonselection)
        doc.AddUndo(c4d.UNDOTYPE_NEW, selectionTag)

        # Checks if there was no error during the creation of the selection tag
        if selectionTag is None:
            raise RuntimeError("couldn't create the selection tag")

        # Retrieves the BaseSelect of the tag so we can copy to that destination
        selTag = selectionTag.GetBaseSelect()

        # Copies the selected polygon to the just created selection tag
        selection.CopyTo(selTag)

        # Sets the name of the selection tag to the texture name
        selectionTag[c4d.ID_BASELIST_NAME] = textureName

        # Adds that selection tag's name to the restriction of the texture ta
        textureTag[c4d.TEXTURETAG_RESTRICTION] = textureName
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, textureTag)

        return True


def main():
    # Retrieves the selected object in the current document.
    flag = c4d.GETACTIVEOBJECTFLAGS_NONE if c4d.GetC4DVersion() > 20000 else c4d.GETACTIVEOBJECTFLAGS_0
    objList = doc.GetActiveObjects(flag)
    if not objList:
        raise RuntimeError("Failed to retrieve selected objects.")

    matList = doc.GetActiveMaterials()
    if not matList:
        raise RuntimeError("Failed to retrieve selected materials.")

    # Checks if the document's mode is polygon so we will apply the mat to only the selected polygons
    onlyToSelection = doc.GetMode() == c4d.Mpolygons

    doc.StartUndo()
    for obj in objList:
        AssignMatToObject(obj, matList, onlyToSelection)

    doc.EndUndo()

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


# Execute main()
if __name__ == '__main__':
    main()
