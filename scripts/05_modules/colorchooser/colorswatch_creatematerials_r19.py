"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Reads all the colors from the first swatch group in the active document and creates material for each one.

Class/method highlighted:
    - c4d.modules.colorchooser.SwatchData
    - c4d.modules.colorchooser.SwatchGroup

Compatible:
    - Win / Mac
    - R19, R20, R21, S22
"""
import c4d


def main():

    # Creates a swatch data
    swatchData = c4d.modules.colorchooser.ColorSwatchData()
    if swatchData is None:
        raise MemoryError("Failed to create a ColorSwatchData.")

    # Loads the swatches data from the active document
    if not swatchData.Load(doc):
        raise RuntimeError("Failed to load the ColorSwatchData.")

    # Makes sure the document contains at least a swatch group
    if swatchData.GetGroupCount(c4d.SWATCH_CATEGORY_DOCUMENT) == 0:
        raise RuntimeError("There is no color swatch stored in the document.")

    # Retrieves the first swatch group
    group = swatchData.GetGroupAtIndex(0, c4d.SWATCH_CATEGORY_DOCUMENT)
    if group is None:
        raise RuntimeError("Failed to retrieve the first Group of the color swatch.")

    groupName = group.GetName()
    colorCount = group.GetColorCount()
    for colorIndex in range(colorCount):
        # Gets the current color
        color = group.GetColor(colorIndex)[0]

        # Creates a material for the current color
        mat = c4d.BaseMaterial(c4d.Mmaterial)
        # Sets the name with the group name and color index
        mat.SetName(groupName + str(colorIndex))

        # Converts maxon.ColorA to c4d.Vector to set the material color
        mat[c4d.MATERIAL_COLOR_COLOR] = c4d.Vector(color.r, color.g, color.b)

        # Inserts the material into the active document
        doc.InsertMaterial(mat)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
