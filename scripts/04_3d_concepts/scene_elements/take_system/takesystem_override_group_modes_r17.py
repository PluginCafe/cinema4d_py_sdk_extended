"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Adds the currently selected objects to a new group in the current Take.

Note:
    The objects of this group will only be visible in the renderer but not in the editor.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.GetCurrentTake()
    - BaseTake.AddOverrideGroup()
    - BaseOverrideGroup.AddToGroup()

Compatible:
    - Win / Mac
    - R17, R18, R19, R20, R21, S22, R23
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

    # Gets the active Take
    take = takeData.GetCurrentTake()
    if take is None:
        raise RuntimeError("Failed to retrieve the current take.")

    # Adds an override Group
    group = take.AddOverrideGroup()
    if group is None:
        raise RuntimeError("Failed to create override group.")

    # Defines the name and render enable state
    group.SetName("Render Objects")
    group.SetEditorMode(c4d.MODE_OFF)
    group.SetRenderMode(c4d.MODE_ON)

    # Add selected object to this group
    for obj in objects:
        group.AddToGroup(takeData, obj)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
