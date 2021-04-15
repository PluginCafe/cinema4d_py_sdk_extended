"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Checks if the current Take is the main Take. If not, the main Take becomes the current Take.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.GetCurrentTake()
    - TakeData.GetMainTake()
    - TakeData.SetCurrentTake()

"""
import c4d


def main():
    # Gets the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Gets the active Take and check it's not the main one
    take = takeData.GetCurrentTake()
    if take.IsMain():
        raise RuntimeError("The selected take is already the main one.")

    # Gets the main Take and set it active
    mainTake = takeData.GetMainTake()
    takeData.SetCurrentTake(mainTake)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
