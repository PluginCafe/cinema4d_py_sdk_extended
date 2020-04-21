"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Synchronizes the keys for the tracks of the active cube's "Size" parameter.

Note:
    - If a track has a key at a certain time, keys for the other synchronized tracks will be created.

Class/method highlighted:
    - BaseObject.SynchronizeVectorTrackKeys()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21, S22
"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Synchronizes keys
    op.SynchronizeVectorTrackKeys(c4d.PRIM_CUBE_LEN, False)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
