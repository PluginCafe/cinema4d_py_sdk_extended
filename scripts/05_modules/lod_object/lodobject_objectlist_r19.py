"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Configures the active LOD object to use "Manual Groups".
    - The selected objects referenced in the objects list are moved under the LOD object and are referenced in each group.

Class/method highlighted:
    - LodObject.GetManualModeObjectListDescID()

Compatible:
    - Win / Mac
    - R19, R20, R21
"""
import c4d


def main():
    # Gets selected objects and check if there is more than 1 object selected
    activeObjects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    if not activeObjects:
        raise RuntimeError("Failed to retrieve selected objects.")

    # Gets the last object selected
    lodObject = doc.GetTargetObject()
    if not lodObject.CheckType(c4d.Olod):
        raise TypeError("last selected object is not a Lod Object.")

    # Defines parameters
    lodObject[c4d.LOD_MODE] = c4d.LOD_MODE_MANUAL_GROUPS
    lodObject[c4d.LOD_CRITERIA] = c4d.LOD_CRITERIA_MANUAL
    lodObject[c4d.LOD_LEVEL_COUNT_DYN] = len(activeObjects) - 1

    level = 0
    # Iterates over all active object
    for obj in activeObjects:

        if obj == lodObject:
            continue

        # Makes object a child object of the LOD object
        obj.Remove()
        doc.InsertObject(obj, lodObject)

        # Inserts object into "Objects" list of the given level
        listID = lodObject.GetManualModeObjectListDescID(level)
        if listID is None:
            continue

        # Creates InExcludeData
        inExData = c4d.InExcludeData()
        if inExData is None:
            continue

        # Inserts object into list
        inExData.InsertObject(obj, 1)

        # Sets parameter
        lodObject[listID] = inExData

        # Increments the level
        level = level + 1

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()