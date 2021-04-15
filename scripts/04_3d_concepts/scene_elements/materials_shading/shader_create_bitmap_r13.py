"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam.

Description:
    - Creates a standard c4d Material.
    - Creates a bitmap shader.

Class/method highlighted:
    - c4d.Material
    - c4d.BaseShader
    - Material.InsertShader()

"""
import c4d


def main():
    # Creates a Standard C4D Material
    mat = c4d.Material()
    if mat is None:
        raise RuntimeError("Failed to create a new default material.")

    # Creates a bitmap shader
    sha = c4d.BaseList2D(c4d.Xbitmap)
    if sha is None:
        raise RuntimeError("Failed to create a bitmap shader.")

    # Defines the path of the bitmap shader
    sha[c4d.BITMAPSHADER_FILENAME] = "FileName"

    # Defines the material color shader to new created one.
    mat[c4d.MATERIAL_COLOR_SHADER] = sha

    # Inserts the shader into the material
    mat.InsertShader(sha)

    # Inserts a material in the active doc
    doc.InsertMaterial(mat)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
