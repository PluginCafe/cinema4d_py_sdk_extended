"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Create a Spherical Volume filled with gradient data.

Class/method highlighted:
    - Ovolume.SetVolume()
    - maxon.frameworks.volume.VolumeToolsInterface.CreateSphereVolume()
    - maxon.frameworks.volume.VolumeToolsInterface.CreateGradient()

"""
import c4d
import maxon
from maxon.frameworks import volume


def main():

    # Creates a Volume Object
    volumeObj = c4d.BaseObject(c4d.Ovolume)
    if volumeObj is None:
        raise MemoryError("Failed to create a volume object.")

    # Creates a Sphere Volume
    sphereVolume = maxon.frameworks.volume.VolumeToolsInterface.CreateSphereVolume(maxon.Float(100.0),
                                                                                   maxon.Vector(0, 100, 0),
                                                                                   maxon.Float(1.0),
                                                                                   maxon.Int32(2),
                                                                                   maxon.ThreadRef(),
                                                                                   None)

    # Fills the volume with a Gradient
    gradientVolume = maxon.frameworks.volume.VolumeToolsInterface.CreateGradientVolume(sphereVolume, maxon.ThreadRef())

    # Sets the VolumeRef in the Volume Object and insert it in the scene
    volumeObj.SetVolume(gradientVolume)
    doc.InsertObject(volumeObj)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
