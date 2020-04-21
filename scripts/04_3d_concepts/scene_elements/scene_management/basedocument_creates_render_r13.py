"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a new temporary BaseDocument with selected objects.
    - Renders it and delete it.

Class/method highlighted:
    - c4d.documents.IsolateObjects()
    - c4d.documents.RenderDocument()
    - c4d.documents.KillDocument()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22
"""
import c4d


def main():
    # Checks if the user selected an object
    objList = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    if not objList:
        raise ValueError("objList is empty or none, please select at least one object.")

    # Creates a new temporary document with all objects previously selected
    tempDoc = c4d.documents.IsolateObjects(doc, objList)
    if tempDoc is None:
        raise RuntimeError("Failed to isolate objects.")

    # Defines the render setting, and set the active render engine to Preview Hardware
    rd = c4d.documents.RenderData()
    rd[c4d.RDATA_RENDERENGINE] = c4d.RDATA_RENDERENGINE_PREVIEWHARDWARE

    # Creates a Bitmaps that will store the render result
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise RuntimeError("Failed to create the bitmap.")

    # Initializes the BaseBitmap
    if bmp.Init(x=int(rd[c4d.RDATA_XRES]), y=int(rd[c4d.RDATA_YRES]), depth=24) != c4d.IMAGERESULT_OK:
        raise RuntimeError("Failed to initialize the bitmap.")

    # Renders the document
    if c4d.documents.RenderDocument(tempDoc, rd.GetData(), bmp, c4d.RENDERFLAGS_EXTERNAL) != c4d.RENDERRESULT_OK:
        raise RuntimeError("Failed to render the temporary document.")

    # Frees the temporary document, means that all objects from this document are no longer alive.
    c4d.documents.KillDocument(tempDoc)

    # Displays the rendered picture
    c4d.bitmaps.ShowBitmap(bmp)


if __name__ == "__main__":
    main()
