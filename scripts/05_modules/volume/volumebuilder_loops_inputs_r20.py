"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Iterates over all input of a Volume Builder.

Class/method highlighted:
    - c4d.Ovolumebuilder
    - VolumeBuilder.GetInputObject()
    - VolumeBuilder.InputObjectIsChild()

Compatible:
    - Win / Mac
    - R20, R21, S22
"""
import c4d


def main():
    # Checks if there is an active object
    if op is None:
        raise ValueError("op is None, please select one object.")

    # Checks if the selected object is a volume builder
    if not op.IsInstanceOf(c4d.Ovolumebuilder):
        raise TypeError("op is not a cd.Ovolumebuilder.")

    # Retrieves the count of object used in the volume builder
    inputCount = op.GetInputObjectCount()
    if inputCount == 0:
        raise RuntimeError("There is no input object for this volume builder.")

    # Iterates over all objects used in the volume builder
    for i in range(inputCount):
        # Retrieves the object
        inputObject = op.GetInputObject(i)
        if inputObject is None: continue

        # Prints the names and if it's a child of something else in the volume builder
        name = inputObject.GetName()
        print(name)

        if op.InputObjectIsChild(i):
            print("child object")


if __name__ == '__main__':
    main()
