"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam.

Description:
    - Creates a standard c4d Material.
    - Creates a new GGX layer.
    - Defines some reflectance parameters.

Class/method highlighted:
    - c4d.Material
    - c4d.ReflectionLayer
    - Material.RemoveReflectionLayerIndex()
    - Material.AddReflectionLayer()
    - ReflectionLayer.GetDataID()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Creates a standard C4D Material
    mat = c4d.Material()
    if mat is None:
        raise RuntimeError("Failed to create a new default material.")

    # Removes the default specular layer
    mat.RemoveReflectionLayerIndex(0)

    # Adds a layer
    layer = mat.AddReflectionLayer()
    if layer is None:
        raise RuntimeError("Failed to create a new reflection layer.")

    # Sets the Layer to GGX mode
    mat[layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_DISTRIBUTION] = c4d.REFLECTION_DISTRIBUTION_GGX

    # Defines the Roughness float value
    mat[layer.GetDataID() + c4d.REFLECTION_LAYER_MAIN_VALUE_ROUGHNESS] = 0.75

    # Defines the layer color value
    mat[layer.GetDataID() + c4d.REFLECTION_LAYER_COLOR_COLOR] = c4d.Vector(1, 0.25, 0.25)

    # Inserts a material in the active doc
    doc.InsertMaterial(mat)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
