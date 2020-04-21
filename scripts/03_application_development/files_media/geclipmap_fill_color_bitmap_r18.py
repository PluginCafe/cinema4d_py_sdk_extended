"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Adds an overlay color to a Picture.

Class/method highlighted:
    - c4d.bitmaps.BaseBitmap
    - c4d.bitmaps.GeClipMap
    - GeClipMap.FillRect()
    - GeClipMap.SetDrawMode()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21, S22
"""
import c4d


def FillBitmapWithColor(srcBmp, rgba):
    if not isinstance(srcBmp, c4d.bitmaps.BaseBitmap):
        raise TypeError("Expected a BaseBitmap")
    if not isinstance(rgba, c4d.Vector4d):
        raise TypeError("Expected a Vector4d")

    # Creates GeClipMap to do some drawing operation
    geClipMap = c4d.bitmaps.GeClipMap()
    if geClipMap is None:
        raise RuntimeError("Failed to create a GeClipMap")

    # Initializes the GeClipMap with our Bitmap
    if not geClipMap.InitWithBitmap(srcBmp, None):
        raise RuntimeError("Failed to initialize GeClipMap")

    # Retrieves the weight and height of our picture
    w, h = geClipMap.GetDim()

    # Start the drawing
    geClipMap.BeginDraw()

    # Defines the raw mode to blend (means we do not override existing pixel and use opacity)
    geClipMap.SetDrawMode(c4d.GE_CM_DRAWMODE_BLEND, c4d.GE_CM_SRC_MAX_OPACITY)

    # Defines the colors used to paint a rectangle
    geClipMap.SetColor(rgba.x, rgba.y, rgba.z, rgba.w)

    # Paints a rectangle into all the pictures
    geClipMap.FillRect(0, 0, w, h)

    # End the drawing
    geClipMap.EndDraw()

    return geClipMap


def main():
    # Opens a Dialog to choose a picture file
    bitmapPath = c4d.storage.LoadDialog(type=c4d.FILESELECTTYPE_IMAGES, title="Please Choose an Image:")
    if not bitmapPath:
        return

    # Loads the picture as a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp.InitWith(bitmapPath)[0] != c4d.IMAGERESULT_OK:
        raise RuntimeError("Failed to load the Picture")

    # Retrieves a GeClipMap multiplied with a color. Value are from 0 to 255 for red, blue, green, alpha
    geClip = FillBitmapWithColor(bmp, c4d.Vector4d(100.0, 0.0, 0, 100.0))

    # Displays the Bitmap stored in the GeClipMap into the Picture Viewer
    c4d.bitmaps.ShowBitmap(geClip.GetBitmap())


if __name__ == "__main__":
    main()
