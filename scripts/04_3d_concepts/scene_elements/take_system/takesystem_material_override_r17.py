"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Creates 10 Takes with different overrides of the material color.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.AddTake()
    - BaseTake.FindOrAddOverrideParam()
    - BaseOverride.UpdateSceneNode()

Compatible:
    - Win / Mac
    - R17, R18, R19, R20, R21, S22
"""
import c4d


def main():
    # Get the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Gets the selected material
    material = doc.GetActiveMaterial()
    if material is None:
        raise RuntimeError("There is no active material.")

    # Checks if it's a default Cinema 4D Material
    if not material.CheckType(c4d.Mmaterial):
        raise TypeError("The material is not a default material.")

    # Makes 10 variations of this material
    for i in range(10):
        # Creates a Take
        takeName = "Variation " + str(i)
        materialVariation = takeData.AddTake(takeName, None, None)
        if materialVariation is None:
            continue

        # Gets the DescID corresponding to the diffuse color of a material
        materialColorParameter = c4d.DescID(c4d.DescLevel(c4d.MATERIAL_COLOR_COLOR, c4d.DTYPE_COLOR, 0))

        # Defines a color
        hsv = c4d.Vector(float(i) * 0.1, 1.0, 1.0)
        rgb = c4d.utils.HSVToRGB(hsv)

        # Overrides the color parameter with the color value
        overrideNode = materialVariation.FindOrAddOverrideParam(takeData, material, materialColorParameter, rgb)

        # Checks everything is correct and updates the scene with the new Take
        if overrideNode is not None:
            overrideNode.UpdateSceneNode(takeData, materialColorParameter)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
