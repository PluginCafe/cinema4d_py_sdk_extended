"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a sphere volume with the corresponding command.

Class/method highlighted:
    - c4d.modules.volume.SendVolumeCommand()
    - c4d.VOLUMECOMMANDTYPE_CREATESPHEREVOLUME

Compatible:
    - Win / Mac
    - R20, R21, S22
"""
import c4d


def main():
    # Configures settings for sphere volume command
    settings = c4d.BaseContainer()
    settings[c4d.CREATESPHEREVOLUMESETTINGS_RADIUS] = 100.0
    settings[c4d.CREATESPHEREVOLUMESETTINGS_POSITION] = c4d.Vector(0, 100, 0)
    settings[c4d.CREATESPHEREVOLUMESETTINGS_BANDWIDTH] = 2
    settings[c4d.CREATESPHEREVOLUMESETTINGS_GRIDSIZE] = 1.0

    # Creates sphere volume
    result = c4d.modules.volume.SendVolumeCommand(c4d.VOLUMECOMMANDTYPE_CREATESPHEREVOLUME, [], settings, doc)
    if not result:
        raise MemoryError("Failed to create a sphere volume.")

    # Gets the sphere volume result
    volumeObject = result[0]

    # Inserts the object into the active document
    doc.InsertObject(volumeObject)
    doc.SetActiveObject(volumeObject)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


# Execute main()
if __name__ == '__main__':
    main()
