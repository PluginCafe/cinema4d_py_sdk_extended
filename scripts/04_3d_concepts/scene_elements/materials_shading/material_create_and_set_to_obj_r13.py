"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam.

Description:
    - Creates a new material.
    - Sets the material to the first texture tag (it's created if it does not exist) of the active object.

Class/method highlighted:
    - c4d.BaseMaterial
    - BaseDocument.InsertMaterial()
    - BaseObject.GetTag()
    - BaseObject.MakeTag()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21
"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Creates a default Cinema 4D Material, the created material only exist in the memory
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    if mat is None:
        raise RuntimeError("Failed to create a new BaseMaterial.")

    # Inserts the material in the active document
    doc.InsertMaterial(mat)

    # Checks if there is already a texture tag on the active object, if not creates it
    textureTag = op.GetTag(c4d.Ttexture)
    if not textureTag:
        textureTag = op.MakeTag(c4d.Ttexture)

    # If the texture tag is not available at this point, something went wrong
    if textureTag is None:
        raise RuntimeError("Failed to retrieve the texture tag.")

    # Links the newly created material from the textureTag Material link parameter
    textureTag[c4d.TEXTURETAG_MATERIAL] = mat

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()