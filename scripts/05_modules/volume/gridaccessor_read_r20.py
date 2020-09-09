"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Reads the Float value of the first channel available from a Volume stored in a Volume Builder.

Class/method highlighted:
    - maxon.frameworks.volume.GridAccessorInterface
    - GridAccessorRef.GetValue()

Compatible:
    - Win / Mac
    - R20, R21, S22, R23
"""
import c4d
import maxon
from maxon.frameworks import volume


def main():
    # Checks if there is an active object
    if op is None:
        raise RuntimeError("Failed to retrieve op.")

    # Checks if the active object is a Volume builder
    if not op.IsInstanceOf(c4d.Ovolumebuilder):
        raise TypeError("op is not a c4d.Ovolumebuilder.")

    # Gets the C4D Volume Object from the cache
    cache = op.GetCache()
    if cache is None:
        raise RuntimeError("Failed to retrieve the cache of the volume builder.")

    # Checks if the cache is a C4D Volume Object
    if not cache.IsInstanceOf(c4d.Ovolume):
        raise TypeError("cache is not a c4d.Ovolume.")

    # Gets the Volume object linked to this Ovolume object.
    volume = cache.GetVolume()
    if volume is None:
        raise RuntimeError("Failed to retrieve the maxon.frameworks.volume.VolumeRef.")

    # Initializes a Float Grid with our existing volume data
    access = maxon.frameworks.volume.GridAccessorInterface.Create(maxon.Float32)
    access.Init(volume)

    # Reads the Float value stored at the c4d.Vector(0, 0, 0) position
    vec = c4d.Vector(0, 0, 0)
    value = access.GetValue(vec)

    print(value)


if __name__ == '__main__':
    main()
