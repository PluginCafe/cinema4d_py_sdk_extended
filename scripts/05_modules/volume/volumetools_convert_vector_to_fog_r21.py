"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a vector volume from scratch.
    - Converts this vector volume to a fog volume.
    - Inserts this fog volume as a child of a volume mesher.

Class/method highlighted:
    - maxon.frameworks.volume.VolumeToolsInterface.CreateNewVector32Volume()
    - maxon.frameworks.volume.GridAccessorInterface
    - GridAccessorRef.InitWithWriteAccess()
    - GridAccessorRef.SetValue()
    - maxon.frameworks.volume.VolumeToolsInterface.ConvertVectorToFog()
    - c4d.VolumeObject
    - VolumeObject.SetVolume()

Compatible:
    - Win / Mac
    - R21, S22
"""
import c4d
import maxon
from maxon.frameworks import volume


def CreateVectorVolume(vectorValue):
    """
    Creates a VolumeRef defined as a vector volume, with a cube of 20 cm filled with the vector value passed.

    :param vectorValue: The vector value to set.
    :type vectorValue: maxon.Vector32
    :return: The created Vector volume with the value defined inside.
    :rtype: maxon.frameworks.volume.VolumeRef
    """
    # Creates volume
    volumeRef = maxon.frameworks.volume.VolumeToolsInterface.CreateNewVector32Volume(maxon.Vector32(0.0))
    if volumeRef is None:
        raise MemoryError("Failed to create a float32 volume.")

    # Creates accessor
    access = maxon.frameworks.volume.GridAccessorInterface.Create(maxon.Vector32)
    if access is None:
        raise RuntimeError("Failed to retrieve the grid accessor.")

    # Initializes the grid for write access
    access.InitWithWriteAccess(volumeRef)

    # Sets values
    size = 20
    for x in range(size):
        for y in range(size):
            for z in range(size):
                pos = maxon.IntVector32(x, y, z)
                access.SetValue(pos, vectorValue)

    return volumeRef


def CreateVectorObject(volumeRef, name):
    """
    Creates a c4d.VolumeObject with the VolumeRef passed.
    Names this VolumeObject with the passed argument.

    :param volumeRef: The VolumeRef to use within the VolumeObject.
    :type volumeRef: maxon.frameworks.volume.VolumeRef
    :param name: The name of the inserted object into the scene.
    :type name: str
    :return: The created VolumeObject
    :rtype: c4d.VolumeObject
    """
    # Creates VolumeObject
    volumeObj = c4d.BaseObject(c4d.Ovolume)
    if volumeObj is None:
        raise MemoryError("Failed to create a volume object.")

    # Names the VolumeObject
    volumeObj.SetName(name)

    # Inserts volume in the VolumeObject
    volumeObj.SetVolume(volumeRef)

    return volumeObj


def main():
    # Creates a VectorVolume
    vecVolumeRef = CreateVectorVolume(maxon.Vector32(100.0))

    # Inserts these vector volume into a VolumeObject
    vecVolumeObj = CreateVectorObject(vecVolumeRef, "Vector Volume")

    # Mixes both vector volume together using cross product
    fogVolumeRef = volume.VolumeToolsInterface.ConvertVectorToFog(vecVolumeRef, maxon.ThreadRef())

    # Inserts the mixed volume into the scene
    fogVolumeObj = CreateVectorObject(fogVolumeRef, "Fog Volume")

    # Creates a VolumeMesher and adds the volumeObject
    volumeMesher = c4d.BaseObject(c4d.Ovolumemesher)
    if volumeMesher is None:
        raise MemoryError("Failed to create a volume mesher object.")

    # Inserts the fog volume object under the volume mesher
    fogVolumeObj.InsertUnder(volumeMesher)

    # Inserts the volume mesher within the scene
    doc.InsertObject(volumeMesher, None, None)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
