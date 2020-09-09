"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a volume from the selected spline object.

Class/method highlighted:
    - c4d.modules.volume.SendVolumeCommand()
    - c4d.VOLUMECOMMANDTYPE_SPLINETOVOLUME

Compatible:
    - Win / Mac
    - R20, R21, S22, R23
"""
import c4d


def main():
    # Checks if there is an active object
    if op is None:
        raise ValueError("op is None, please select one object.")

    # Checks if the selected object is a spline object
    if not op.IsInstanceOf(c4d.Ospline):
        raise TypeError("op is not a c4d.Ospline.")

    # Initializes an object list and adds the spline
    objects = list()
    objects.append(op)

    # Configures settings to create the spline volume
    settings = c4d.BaseContainer()
    settings[c4d.SPLINETOVOLUMESETTINGS_GRIDSIZE] = 1.0
    settings[c4d.SPLINETOVOLUMESETTINGS_BANDWIDTH] = 3
    settings[c4d.SPLINETOVOLUMESETTINGS_RADIUS] = 1.0
    settings[c4d.SPLINETOVOLUMESETTINGS_DENSITY] = 1.0

    # Creates spline volume
    result = c4d.modules.volume.SendVolumeCommand(c4d.VOLUMECOMMANDTYPE_SPLINETOVOLUME, objects, settings, doc)
    if not result:
        RuntimeError("Failed to convert a spline to a volume.")

    # Retrieves the spline to volume result
    volumeObject = result[0]

    # Inserts the object into the active document
    doc.InsertObject(volumeObject)
    doc.SetActiveObject(volumeObject)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
