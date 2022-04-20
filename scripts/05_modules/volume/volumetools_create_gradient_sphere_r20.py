"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Create a Spherical Volume filled with gradient data.

Class/method highlighted:
    - Ovolume.SetVolume()
    - maxon.VolumeToolsInterface.CreateSphereVolume()
    - maxon.VolumeToolsInterface.CreateGradient()

"""
import c4d
import maxon


def main():

    # Creates a Volume Object
    volumeObj = c4d.BaseObject(c4d.Ovolume)
    if volumeObj is None:
        raise MemoryError("Failed to create a volume object.")

    # Creates a Sphere Volume
    sphereVolume = maxon.VolumeToolsInterface.CreateSphereVolume(maxon.Float(100.0),
                                                                 maxon.Vector(0, 100, 0),
                                                                 maxon.Float(1.0),
                                                                 maxon.Int32(2),
                                                                 maxon.ThreadRef(),
                                                                 None)

    # Fills the volume with a Gradient
    gradientVolume = maxon.VolumeToolsInterface.CreateGradientVolume(sphereVolume, maxon.ThreadRef())

    # Sets the VolumeRef in the Volume Object and insert it in the scene
    volumeObj.SetVolume(gradientVolume)
    doc.InsertObject(volumeObj)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
