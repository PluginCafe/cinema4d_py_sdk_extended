"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Checks the current criteria of the active LOD object 'op'.
    - If it is "User LOD Level" the current level is set to the maximum level.

Class/method highlighted:
    - LodObject.GetLevelCount()

Compatible:
    - Win / Mac
    - R19, R20, R21
"""
import c4d


def main():
    # Checks if there is an active object
    if op is None:
        raise RuntimeError("Failed to retrieve the active object.")

    # Checks if active object is a LOD object
    if not op.CheckType(c4d.Olod):
        raise TypeError("op is not a Lod Object.")

    # Gets current criteria from active LOD object
    criteria = op[c4d.LOD_CRITERIA]

    # Checks if User LOD Level
    if criteria == c4d.LOD_CRITERIA_MANUAL:

        # Gets maximum level
        maxLevel = op.GetLevelCount() - 1

        # Sets current level to max level
        op[c4d.LOD_CURRENT_LEVEL] = maxLevel

        # Pushes an update event to Cinema 4D
        c4d.EventAdd()


if __name__ == '__main__':
    main()