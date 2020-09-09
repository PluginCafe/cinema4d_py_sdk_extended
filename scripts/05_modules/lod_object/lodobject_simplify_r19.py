"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Configures the active LodObject 'op' to use the "Simplify" mode.
    - The first level uses the "Convex Hull" mode, the second the "Null" mode.
    - The second level uses the "Simplify" mode and a manual number of levels.

Class/method highlighted:
    - LodObject.GetLevelCount()

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

    # Defines some parameters
    op[c4d.LOD_MODE] = c4d.LOD_MODE_SIMPLIFY
    op[c4d.LOD_CRITERIA] = c4d.LOD_CRITERIA_MANUAL
    op[c4d.LOD_LEVEL_COUNT_DYN] = 2
    op[c4d.LOD_CURRENT_LEVEL] = 0

    # Gets first level
    descID = op.GetSimplifyModeDescID(0)
    if descID is not None:
        # Sets mode to "Convex Hull"
        op[descID] = c4d.LOD_SIMPLIFY_CONVEXHULL

        descID = op.GetPerObjectControlDescID(0)
        if descID is not None:
            # Sets "Per Object" to True
            op[descID] = True

    # Gets second level
    descID = op.GetSimplifyModeDescID(1)
    if descID is not None:
        # Sets mode to "Null"
        op[descID] = c4d.LOD_SIMPLIFY_NULL

        descID = op.GetNullDisplayDescID(1)
        if descID is not None:
            # Sets "Display" to "Circle"
            op[descID] = c4d.NULLOBJECT_DISPLAY_CIRCLE

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
