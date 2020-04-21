"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Reads the color value from the active material.
    - Calculates the complementary color and applies it to new material.

Class/method highlighted:
    - c4d.modules.colorchooser.ColorHarmonyGetComplementary()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21, S22
"""
import c4d


def main():
    # Retrieves active material
    mat = doc.GetActiveMaterial()
    if mat is None:
        raise RuntimeError("Failed to retrieve the selected material.")

    # Checks active material is a standard material
    if not mat.IsInstanceOf(c4d.Mmaterial):
        raise TypeError("The selected material is not a default c4d material.")

    # Retrieves the material's color
    color = mat[c4d.MATERIAL_COLOR_COLOR]
    if color is None:
        raise RuntimeError("Unable to retrieve the color of the color channel.")

    # Calculates the complementary color
    res = c4d.modules.colorchooser.ColorHarmonyGetComplementary(color, False)
    if not res:
        raise RuntimeError("Failed to retrieve the complementary color.")

    # Retrieves the complementary color
    complementaryColor = res[1]

    # Creates a new material with complementary color
    complementaryMat = c4d.BaseMaterial(c4d.Mmaterial)
    if complementaryMat is None:
        raise MemoryError("Failed to create a new default base material.")

    # Sets the complementary color as material's color
    complementaryMat[c4d.MATERIAL_COLOR_COLOR] = complementaryColor

    # Inserts the material with complementary color into the active document
    doc.InsertMaterial(complementaryMat)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
