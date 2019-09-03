"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Loads a VDB file to a c4d.VolumeObject.

Class/method highlighted:
    - maxon.Url
    - maxon.DataDictionary
    - maxon.frameworks.volume.VolumeToolsInterface.LoadVDBFile()

Compatible:
    - Win / Mac
    - R20, R21
"""
import c4d
import maxon
from maxon.frameworks import volume


def main():
    # Retrieves a path to load the imported file
    selectedFile = c4d.storage.LoadDialog(title="Load File for Volume Import", type=c4d.FILESELECTTYPE_ANYTHING, force_suffix="vdb")
    if not selectedFile:
        return

    # Define the path of the file.vdb located in the same folder of this script
    path = maxon.Url(selectedFile)

    # Try to load the VDB File, and apply a Scale of 1 to this VDB
    scale = 1.0
    gridNames = maxon.BaseArray(maxon.String)
    gridIndices = None
    metaData = maxon.DataDictionary()
    volumeArr = None
    try:
        volumeArr = maxon.frameworks.volume.VolumeToolsInterface.LoadVDBFile(path, scale, gridNames, gridIndices, metaData)
    except Exception as e:
        print "LoadVDBFile error {}, {}".format(e.message, e.args)

    if volumeArr is None:
        raise RuntimeError("Unknown error.")

    if len(volumeArr) == 0:
        raise RuntimeError("Selected Vdb store 0 volume.")

    # Retrieves the first volume
    volRef = volumeArr[0]

    # Creates a Volume Object to store the previous volume calculated
    volumeObj = c4d.BaseObject(c4d.Ovolume)
    if volumeObj is None:
        raise MemoryError("Failed to create a volume object.")

    doc.InsertObject(volumeObj)
    volumeObj.SetVolume(volRef)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()