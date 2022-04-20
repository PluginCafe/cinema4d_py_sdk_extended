"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Create a volume from scratch and assign values to voxels.

Class/method highlighted:
    - maxon.VolumeToolsInterface.CreateNewFloat32Volume()
    - maxon.GridAccessorInterface
    - GridAccessorRef.SetValue()


"""
import c4d
import maxon


def main():
    # Creates VolumeObject
    volumeObj = c4d.BaseObject(c4d.Ovolume)
    if volumeObj is None:
        raise MemoryError("Failed to create a volume object.")

    # Inserts the volume Object within the scene
    doc.InsertObject(volumeObj, None, None)

    # Creates volume
    volume = maxon.VolumeToolsInterface.CreateNewFloat32Volume(0.0)
    if volume is None:
        raise MemoryError("Failed to create a float32 volume.")

    volume.SetGridClass(c4d.GRIDCLASS_FOG)
    volume.SetGridName("Example Grid")

    # Defines the initial matrix of the grid
    scaleMatrix = maxon.Matrix()
    volume.SetGridTransform(scaleMatrix)

    # Creates accessor
    access = maxon.GridAccessorInterface.Create(maxon.Float32)
    if access is None:
        raise RuntimeError("Failed to retrieve the grid accessor.")

    # Initializes the grid for write access, changed with R21
    initMethod = access.Init if c4d.GetC4DVersion() < 21000 else access.InitWithWriteAccess
    initMethod(volume)

    # Sets values in the shape of a helix
    offset = 0.0
    radius = 100.0
    height = 500.0
    step   = 50.0
    stepSize = height / step

    while offset < step:
        sin, cos = c4d.utils.SinCos(offset)
        pos = maxon.IntVector32()
        pos.x = maxon.Int32(sin * radius)
        pos.y = maxon.Int32(cos * radius)
        pos.z = maxon.Int32(offset * stepSize)

        # Sets value
        access.SetValue(pos, 10.0)

        offset = offset + 0.1

    # Inserts volume in the VolumeObject
    volumeObj.SetVolume(volume)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
