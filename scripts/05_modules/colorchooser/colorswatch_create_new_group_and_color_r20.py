"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a swatch group and adds rainbow colors to it.

Class/method highlighted:
    - c4d.modules.colorchooser.SwatchData
    - c4d.modules.colorchooser.SwatchGroup
    - maxon.ColorA

Compatible:
    - Win / Mac
    - R20, R21, S22, R23
"""
import c4d
import maxon


def main():

    # Creates a swatch data
    swatchData = c4d.modules.colorchooser.ColorSwatchData()
    if swatchData is None:
        raise MemoryError("Failed to create a ColorSwatchData.")

    # Loads the swatch data from the active document
    if not swatchData.Load(doc):
        raise RuntimeError("Failed to load the ColorSwatchData.")

    # Creates a swatch group
    group = swatchData.AddGroup(c4d.SWATCH_CATEGORY_DOCUMENT, "Rainbow")
    if group is None:
        raise MemoryError("Failed to create a group.")

    for i in range(20):

        # Creates rainbow colors and stores them in the previously created group
        hsv = c4d.Vector(float(i) * 0.05, 1.0, 1.0)
        rgb = c4d.utils.HSVToRGB(hsv)

        # Creates a maxon.ColorA for the current color
        col4 = maxon.ColorA()
        col4.r = rgb.x
        col4.g = rgb.y
        col4.b = rgb.z
        col4.a = 1.0
        group.AddColor(col4)

    # Inserts the swatch group in the last position
    index = swatchData.GetGroupCount(c4d.SWATCH_CATEGORY_DOCUMENT) - 1
    swatchData.SetGroupAtIndex(index, group)

    # Saves the group into the active document
    swatchData.Save(doc)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
