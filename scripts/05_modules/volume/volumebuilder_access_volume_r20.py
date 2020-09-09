"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Retrieves a volume object from a volume builder.

Class/method highlighted:
    - c4d.Ovolumebuilder
    - c4d.Ovolume

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
        raise ValueError("op is None, please select one object.")

    # Checks if the selected object is a volume builder
    if not op.IsInstanceOf(c4d.Ovolumebuilder):
        raise TypeError("op is not a c4d.Ovolumebuilder.")

    # Retrieves the volume builder cache
    cache = op.GetCache()
    if cache is None:
        raise RuntimeError("Failed to retrieve the cache.")

    # Checks if the cache object is a volume object
    if not cache.IsInstanceOf(c4d.Ovolume):
        raise TypeError("cache is not a c4d.Ovolume.")

    # Retrieves the core volume interface
    volume = cache.GetVolume()
    if volume is None:
        raise RuntimeError("Failed to retrieve the core volume, most likely there is no volume set.")
    print(volume)

    # Prints the grid name
    gridName = volume.GetGridName()
    print(gridName)


if __name__ == '__main__':
    main()
