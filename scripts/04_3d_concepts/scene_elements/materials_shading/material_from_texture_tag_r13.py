"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam.

Description:
    - Gets the material linked to the first texture tag of the active object.

Class/method highlighted:
    - BaseObject.GetTag()
    - TextureTag.GetMaterial()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22
"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Get the first texture tag
    textureTag = op.GetTag(c4d.Ttexture)
    if textureTag is None:
        raise RuntimeError("Failed to retrieve the texture tag.")

    # Retrieves the linked material
    mat = textureTag.GetMaterial()

    # If no material is linked we leave
    if mat is None:
        return

    # Print the name of the material to the console.
    print(mat.GetName())


if __name__ == '__main__':
    main()
