"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Adds a new color group to the active document.

Note:
    - Take a look at colorswatch_rainbowgroup_r20 for an updated R20 version.

Class/method highlighted:
    - c4d.modules.colorchooser.SwatchData
    - SwatchData.SetGroupAtIndex()

Compatible:
    - Win / Mac
    - R18, R19
"""
import c4d


def main():
    # Creates a new ColorSwatchData
    swatchData = c4d.modules.colorchooser.ColorSwatchData(doc)
    if swatchData is None:
        raise MemoryError("Failed to create a ColorSwatchData.")

    # Adds a group to the newly created ColorSwatchData
    group = swatchData.AddGroup("New Group", False)
    if group is None:
        raise MemoryError("Failed to create a new group.")

    # Adds red, green and blue colors to the ColorSwatchGroup
    group.AddColor(c4d.Vector(1.0, 0.0, 0.0), True)   
    group.AddColor(c4d.Vector(0.0, 1.0, 0.0), False) 
    group.AddColor(c4d.Vector(0.0, 0.0, 1.0), False)

    # Assigns the new group
    swatchData.SetGroupAtIndex(swatchData.GetGroupCount() - 1, group)

    # Saves the color groups into the active document
    swatchData.Save(doc)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
