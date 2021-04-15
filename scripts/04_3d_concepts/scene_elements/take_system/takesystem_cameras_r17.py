"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Creates a new Take for each currently selected camera object.

Class/method highlighted:
    - TakeData.AddTake()

"""
import c4d


def main():
    # Gets the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Gets the currently selected objects
    selectedObjects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)

    # Iterates the selected Objects
    for element in selectedObjects:

        # Checks if the object is a Camera object
        if not element.CheckType(c4d.Ocamera):
            continue

        # Adds a Take for this camera
        cameraTake = takeData.AddTake("Take for Camera " + element.GetName(), None, None)
        if cameraTake is None:
            continue

        # Defines the active camera for this Take
        cameraTake.SetCamera(takeData, element)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
