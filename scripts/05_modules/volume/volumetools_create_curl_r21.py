"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a new vector volume object with a curl filter applied from an existing Volume Builder set as vector mode.

Class/method highlighted:
    - c4d.VolumeObject
    - VolumeObject.GetVolume()
    - maxon.VolumeToolsInterface.CreateCurlVolume()
    - VolumeObject.SetVolume()

"""
import c4d
import maxon


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Checks if the selected object is a volume builder
    if not op.IsInstanceOf(c4d.Ovolumebuilder):
        raise TypeError("op is not a c4d.Ovolumebuilder.")

    # Checks if the volume builder is set a vector since Curl only works with vector volume
    if not op[c4d.ID_VOLUMEBUILDER_VOLUMETYPE] == c4d.ID_VOLUMEBUILDER_VECTOR:
        raise TypeError("Volume buidler is not set as vector volume.")

    # Retrieves the volume builder cache
    cache = op.GetCache()
    if cache is None:
        raise RuntimeError("Failed to retrieve the cache.")

    # Checks if the cache object is a volume object
    if not cache.IsInstanceOf(c4d.Ovolume):
        raise TypeError("cache is not a c4d.Ovolume.")

    # Retrieves the core volume interface
    vecVolume = cache.GetVolume()
    if vecVolume is None:
        raise RuntimeError("Failed to retrieve the core volume, most likely there is no volume set.")

    # Creates a new curl volume based on the vector VolumeRef we retrieved
    curlVecVolume = maxon.VolumeToolsInterface.CreateCurlVolume(vecVolume, maxon.ThreadRef())

    # Creates a Volume Object
    volumeObj = c4d.BaseObject(c4d.Ovolume)
    if volumeObj is None:
        raise MemoryError("Failed to create a volume object.")

    # Defines the VolumeRef used by the VolumeObject
    volumeObj.SetVolume(curlVecVolume)

    # Inserts the volume object into the document
    doc.InsertObject(volumeObj)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
