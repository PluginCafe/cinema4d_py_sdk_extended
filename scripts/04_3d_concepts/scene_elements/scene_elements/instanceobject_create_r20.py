"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Instantiates 100 cubes, with an InstanceObject.
    - Offsets each instances with a custom Matrix.
    - Colorizes each instances with a custom color.

Class/method highlighted:
    - c4d.InstanceObject
    - InstanceObject.SetInstanceMatrices()
    - InstanceObject.SetInstanceColors()

Compatible:
    - Win / Mac
    - R20, R21, S22
"""
import c4d


def main():
    # Creates cube
    cube = c4d.BaseObject(c4d.Ocube)
    if cube is None:
        raise RuntimeError("Failed to create a cube.")

    # Creates instance object
    instance = c4d.InstanceObject()
    if instance is None:
        raise RuntimeError("Failed to create an instance object.")

    # Inserts cube into the active document
    doc.InsertObject(cube, None, None)

    # Inserts instance object into the active document
    doc.InsertObject(instance, None, None)

    # Makes instance object active (selected)
    doc.SetActiveObject(instance)

    # Sets the instance reference object to the created cube
    instance.SetReferenceObject(cube)

    # Sets render instance mode to multi-instance
    instance[c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE] = c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE_MULTIINSTANCE

    # Displays instances as points
    instance[c4d.INSTANCEOBJECT_DRAW_MODE] = c4d.INSTANCEOBJECT_DRAW_MODE_POINTS

    # Initializes multi-instance matrices and colors
    matrices = list()
    colors = list()

    # The number of instances
    count = 100

    # Start position and translation step
    position = 0.0
    step = 300.0

    # Hue start and step
    hue = 0.0
    hueStep = 1.0 / count

    # Generates matrices and colors for 100 instances
    for i in range(count):
        # Calculates the current instance matrix
        matrix = c4d.utils.MatrixMove(c4d.Vector(position, 0.0, 0.0))
        matrices.append(matrix)
        position = position + step

        # Calculates the current instance color
        colorHSV = c4d.Vector(hue, 1.0, 1.0)
        colorRGB = c4d.utils.HSVToRGB(colorHSV)
        colors.append(colorRGB)
        hue = hue + hueStep

    # Stores instance matrices
    instance.SetInstanceMatrices(matrices)

    # Stores instance colors
    instance.SetInstanceColors(colors)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
