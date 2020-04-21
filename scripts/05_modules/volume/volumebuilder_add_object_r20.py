"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a volume builder and adds a cube object to it. Configures cube's object settings.

Class/method highlighted:
    - c4d.Ovolumebuilder
    - c4d.modules.volume.VolumeBuilder

Compatible:
    - Win / Mac
    - R20, R21, S22
"""
import c4d


def main():
    # Creates volume builder object
    volumeBuilder = c4d.BaseObject(c4d.Ovolumebuilder)
    if volumeBuilder is None:
        raise Exception('Could not create Volume Builder object')

    # Inserts volume builder into the active document
    doc.InsertObject(volumeBuilder, None, None)
    doc.SetActiveObject(volumeBuilder)

    # Creates a cube object
    cube = c4d.BaseObject(c4d.Ocube)
    if cube is None:
        raise Exception('Could not create cube object')

    # Inserts cube into the active document
    doc.InsertObject(cube, None, None)

    # Adds cube object to the volume builder
    ret = volumeBuilder.AddSceneObject(cube)
    if not ret:
        raise Exception('Could not add scene object')

    # Retrieves cube's volume builder settings container
    settings = volumeBuilder.GetSettingsContainerForObject(cube)
    if settings is None:
        raise Exception('Could not access settings')

    # Configures cube's settings
    settings[c4d.ID_VOLUMEBUILDER_TAG_USEPOINTS] = True
    settings[c4d.ID_VOLUMEBUILDER_TAG_MESHRADIUS] = 10.0

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
