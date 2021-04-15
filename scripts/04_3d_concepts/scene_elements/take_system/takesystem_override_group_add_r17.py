"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Adds the currently selected objects to the BaseOverrideGroup "group".

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.GetCurrentTake()
    - BaseTake.GetFirstOverrideGroup()
    - BaseOverrideGroup.AddToGroup()

"""
import c4d


def main():
    # Retrieves selected objects
    objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    if not objects:
        raise RuntimeError("There is no objects selected.")

    # Gets the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Gets the active Take and check it's not the main one
    take = takeData.GetCurrentTake()
    if take is None:
        raise RuntimeError("Failed to retrieve the current take.")

    # Retrieves the first overrides groups for this Take
    group = take.GetFirstOverrideGroup()
    if group is None:
        raise RuntimeError("Failed to retrieve the first override group.")

    # Loops through all selected objects and add them to the group
    for obj in objects:
        group.AddToGroup(takeData, obj)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
