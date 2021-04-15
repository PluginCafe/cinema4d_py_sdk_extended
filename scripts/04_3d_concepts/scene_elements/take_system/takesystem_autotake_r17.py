"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Stores edits of the given sphere object in a Take.

Note:
    - If the auto Take mode is enabled, the current Take is used.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - BaseTake.AutoTake()

"""
import c4d


def main():
    # Checks if there is an active object and if it's a Sphere object
    if op is None:
        raise ValueError("op is none, please select one object.")

    if not op.CheckType(c4d.Osphere):
        raise TypeError("The objects is not a sphere.")

    # Stores a copy of this object to use later in the autotake as initial state comparison
    undoObject = op.GetClone(c4d.COPYFLAGS_0)

    # Changes the radius of the sphere in scene
    op[c4d.PRIM_SPHERE_RAD] = 100.0

    # Gets the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Checks if there is some TakeData and the current mode is set to auto Take
    if takeData and takeData.GetTakeMode() == c4d.TAKE_MODE_AUTO:

        # Retrieves the active Take
        currentTake = takeData.GetCurrentTake()

        # If there is an active Take, automatically generate a Take based on the difference between op and undoObject
        if currentTake:
            currentTake.AutoTake(takeData, op, undoObject)

        # Pushes an update event to Cinema 4D
        c4d.EventAdd()


if __name__ == '__main__':
    main()
