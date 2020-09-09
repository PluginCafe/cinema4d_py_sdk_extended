"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Adjusts the active Render Settings to render the current frame based on user settings.

Class/method highlighted:
    - BaseDocument.GetActiveRenderData()

Compatible:
    - Win / Mac
    - R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Retrieves a copy of the current documents render settings
    rd = doc.GetActiveRenderData().GetClone().GetData()
    if rd is None:
        raise RuntimeError("Failed to retrieve the clone of the active Render Settings.")

    # Sets various render parameters
    rd[c4d.RDATA_FRAMESEQUENCE] = 1
    rd[c4d.RDATA_SAVEIMAGE] = False
    rd[c4d.RDATA_MULTIPASS_SAVEIMAGE] = False

    # Gets the x and y res from the render settings
    xRes = int(rd[c4d.RDATA_XRES])
    yRes = int(rd[c4d.RDATA_YRES])

    # Initializes the bitmap with the result size
    # The resolution must match with the output size of the render settings
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise RuntimeError("Failed to create the Bitmap.")

    if bmp.Init(x=xRes, y=yRes) != c4d.IMAGERESULT_OK:
        raise RuntimeError("Failed to initialize the Bitmap.")

    # Calls the renderer
    res = c4d.documents.RenderDocument(doc, rd, bmp, c4d.RENDERFLAGS_EXTERNAL)

    # Leaves if there is an error while rendering
    if res != c4d.RENDERRESULT_OK:
        raise RuntimeError("Failed to render the document.")

    # Displays the bitmap in the Picture Viewer
    c4d.bitmaps.ShowBitmap(bmp)


if __name__ == '__main__':
    main()
