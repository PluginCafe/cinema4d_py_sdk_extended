"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam.

Description:
    - Loops over all shaders of the active material.
    - If it's a LayerShader, loops over all layers and print its name.

Class/method highlighted:
    - c4d.BaseShader
    - c4d.LayerShader
    - c4d.LayerShaderLayer
    - LayerShader.GetFirstLayer()

Compatible:
    - Win / Mac
    - R17, R18, R19, R20, R21
"""
import c4d


def iterateShaders(sha):
    """
    This function iterates over a BaseList2D, BaseShader inherit from BaseList2D.
    If it's a LayerShader, iterates over all layers and print their name.
    :param sha: Shader to iterate.
    """
    while sha:
        # Checks if the shader is a Layer Shader
        if sha.CheckType(c4d.Xlayer):

            # Gets the first layer
            layer = sha.GetFirstLayer()

            # Iterates over all layers
            while layer:
                # Gets the name of the current layer
                layerName = layer.GetName(sha.GetDocument())
                print "layer:{}".format(layerName)

                # Gets the next layer
                layer = layer.GetNext()

        iterateShaders(sha.GetDown())
        sha = sha.GetNext()

def main():
    # Gets the first material
    mat = doc.GetFirstMaterial()

    # Loops until mat variable is a valid object
    while mat:
        # Iterates overs all shaders and starts by the first shader
        iterateShaders(mat.GetFirstShader())

        # Gets the next material, if it's the last material, mat equal None, and then leave the loop
        mat = mat.GetNext()


if __name__ == '__main__':
    main()