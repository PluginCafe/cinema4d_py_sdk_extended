"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Configures the display settings for each level of the active LOD object 'op'.

Class/method highlighted:
    - c4d.LodObject
    - LodObject.GetDisplayBFCDescID()
    - LodObject.GetDisplayStModeDescID()

Compatible:
    - Win / Mac
    - R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Checks if there is an active object
    if op is None:
        raise RuntimeError("Failed to retrieve the active object.")

    # Checks if active object is a LOD object
    if not op.CheckType(c4d.Olod):
        raise TypeError("op is not a Lod Object.")

    # Gets active LOD object number of levels
    levelCount = op.GetLevelCount()

    # Iterates over all levels of LOD
    for level in range(levelCount):
        descID = op.GetDisplayBFCDescID(level)

        # Enables backface culling
        if descID is not None:
            op[descID] = True

        # Uses "Lines" shading
        descID = op.GetDisplayStModeDescID(level)
        if descID is not None:
            op[descID] = c4d.DISPLAYTAG_WDISPLAY_WIREFRAME

        # Uses "Wireframe" style
        descID = op.GetDisplayShModeDescID(level)
        if descID is not None:
            op[descID] = c4d.DISPLAYTAG_SDISPLAY_NOSHADING

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
