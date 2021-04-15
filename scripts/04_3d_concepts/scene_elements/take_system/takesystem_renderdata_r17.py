"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Gets the first Render Setting and loops through all Render Setting objects.
    - Create a Take for each Render Setting.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.AddTake()
    - GeListNode.GetNext()

"""
import c4d


def main():
    # Gets the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Gets the first render Data
    renderData = doc.GetFirstRenderData()

    # Loops over all 1st level render data (render data children of another render data are not processed)
    while renderData:
        # Creates a Take and defines the render data
        renderDataTake = takeData.AddTake("Take for RenderData " + renderData.GetName(), None, None)
        if renderDataTake is not None:
            renderDataTake.SetRenderData(takeData, renderData)

        # Next loop, renderData, will be equal to the next renderData.
        # At the end it will be None, and the loop will leave
        renderData = renderData.GetNext()

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
