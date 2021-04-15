"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Asks for a VDB file to load into a VolumeRef (a VolumeInterface Reference).
    - Insert this VolumeRef into a VolumeObject.
    - Inserts this VolumeObject into the current scene.

Class/method highlighted:
    - maxon.Url
    - maxon.frameworks.VolumeInterface.CreateFromFile()
    - c4d.modules.volume.VolumeObject
    - VolumeObject.SetVolume()

"""
import c4d
import maxon
from maxon.frameworks import volume


def main():
    # Opens a LoadDialog to define the path of the VDB file to load
    filePath = c4d.storage.LoadDialog()

    # Leaves if nothing was selected
    if not filePath:
        return

    # Warn if the selected files is not a .vsb file
    if not filePath.endswith(".vdb"):
        raise TypeError("Selected File is not a VDB file.")

    # Creates a maxon.Url from this path
    url = maxon.Url(filePath)

    # Creates a VolumeRef from the url
    try:
        volumeRef = volume.VolumeInterface.CreateFromFile(url, 1.0, 0)
    except IOError:
        raise IOError("Failed to load the VDB file.")

    # Creates a VolumeObject (the things to insert into the scene)
    vol = c4d.modules.volume.VolumeObject()

    # Defines the VolumeRef of the VolumeObject to the loaded vdb
    vol.SetVolume(volumeRef)

    # Inserts the VolumeObject into the current active scene
    doc.InsertObject(vol)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


# Execute main()
if __name__ == '__main__':
    main()
