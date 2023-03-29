"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam.

Description:
    - Loops over all materials, shaders of the active document and display their previews in the Picture Viewer.

Class/method highlighted:
    - BaseDocument.GetFirstMaterial()
    - GeListNode.GetNext()
    - GeListNode.GetDown()
    - Material.GetPreview()
    - BaseList2D.GetMain()
"""
import c4d


def iterateShaders(sha):
    """This function iterates over a BaseList2D, BaseShader inherit from BaseList2D.

    Args:
        sha (Union[c4d.BaseList2D, c4d.BaseShader]): Shader to iterate.
    """
    while sha:
        matName = sha.GetMain().GetName()
        shaName = sha.GetName()
        print("Mat: {0}, shader:{1}".format(matName, shaName))

        iterateShaders(sha.GetDown())
        sha = sha.GetNext()


def main():
    # Gets the first material
    mat = doc.GetFirstMaterial()

    # Loops until mat variable is a valid object
    while mat:
        # Displays the Material preview to the Picture Viewer
        c4d.bitmaps.ShowBitmap(mat.GetPreview())

        # Iterates overs all shaders and starts by the first shader
        iterateShaders(mat.GetFirstShader())

        # Gets the next material, if it's the last material, mat equal None, and then leave the loop
        mat = mat.GetNext()


if __name__ == '__main__':
    main()
