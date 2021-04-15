"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Reads the color parameter of the given material and prints the value as RGB and HSV.

Class/method highlighted:
    - c4d.modules.colorchooser.ColorRGBToString()
    - c4d.modules.colorchooser.ColorHSVToString()

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

    # Outputs the material's color in RGB and HSV formats
    rgbColorStr = c4d.modules.colorchooser.ColorRGBToString(color)
    hsvColorStr = c4d.modules.colorchooser.ColorHSVToString(color)
    print("Material Color: RGB " + rgbColorStr + " - HSV " + hsvColorStr)


if __name__ == '__main__':
    main()
