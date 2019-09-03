"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a new object buffer multipass.
    - Inserts it into the currently active render setting.

Class/method highlighted:
    - BaseDocument.GetActiveRenderData()
    - RenderData.InsertMultipass()


Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21
"""

import c4d


def main():
    # Retrieves the Active Render Data (Render Settings)
    renderData = doc.GetActiveRenderData()
    if renderData is None:
        raise RuntimeError("Failed to retrieve the active render data.")

    # Creates a MultiPass object, they all get the same plugin ID Zmultipass
    objectBuffer = c4d.BaseList2D(c4d.Zmultipass)
    if objectBuffer is None:
        raise RuntimeError("Failed to create a multipass object.")

    # Defines the type of the MultiPass Object to a object buffer,
    objectBuffer[c4d.MULTIPASSOBJECT_TYPE] = c4d.VPBUFFER_OBJECTBUFFER

    # Defines the ID
    objectBuffer[c4d.MULTIPASSOBJECT_OBJECTBUFFER] = 10

    # Inserts the MultiPass into the MultiPass list of the Render Settings
    renderData.InsertMultipass(objectBuffer)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()