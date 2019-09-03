"""
Copyright: MAXON Computer GmbH

Description:
    - Copies the internal data of a 32 bit per-channel image to a new one.

Note:
    - BaseBitmap.GetClone could be used for doing the exact same purpose, bu

Class/method highlighted:
    - BaseBitmap.SetPixelCnt()
    - BaseBitmap.GetPixelCnt()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21
"""
import c4d


def main():
    # Opens a Dialog to choose a picture file
    path = c4d.storage.LoadDialog(type=c4d.FILESELECTTYPE_IMAGES, title="Please Choose a 32-bit Image:")

    # If the user cancels, leaves
    if not path:
        return

    # Creates a BaseBitmap that will be used for loading the selected picture
    orig = c4d.bitmaps.BaseBitmap()
    if orig is None:
        raise RuntimeError("Failed to create the bitmap.")

    # Initializes the BaseBitmap with the selected picture
    if orig.InitWith(path)[0] != c4d.IMAGERESULT_OK:
        raise RuntimeError("Cannot load image \"" + path + "\".")

    # Checks if channel depth is really 32 bit
    if orig.GetBt()/3 != 32:
        raise RuntimeError("The image \"" + path + "\" is not a 32 bit per-channel image.")

    # Gets selected image information
    width, height = orig.GetSize()
    bits = orig.GetBt()

    # Creates a BaseBitmap that will be ued for making a copy copy and initialize it
    copy = c4d.bitmaps.BaseBitmap()
    if copy is None:
        raise RuntimeError("Failed to create the bitmap.")

    copy.Init(width, height, bits)
    if orig.InitWith(path)[0] != c4d.IMAGERESULT_OK:
        raise RuntimeError("Cannot load image \"" + path + "\".")

    # Calculates the number of bytes per pixel
    # Each pixel has RGB bits, so we need an offset of 'inc' bytes per pixel
    # the image has 32 bits per-channel : (32*3)/8 = 12 bytes per pixel (1 byte = 8 bits)
    # the image has 3 channels per pixel (RGB) : 12/3 = 4 bytes per component = 1 float
    inc = orig.GetBt() / 8

    # Creates a byte sequence buffer large enough to store the copied image pixels
    sq = c4d.storage.ByteSeq(None, width*height*inc)
    if sq is None:
        raise RuntimeError("Failed to create the bytes sequence.")

    # Copy data to our buffer
    for row in xrange(height):
        # Offset on bitmap row + offset bytes per pixel
        bufferAtOffset = sq.GetOffset(row*(width*inc))

        # Read pixels from the original bitmap into the buffer
        orig.GetPixelCnt(0, row, width, bufferAtOffset, inc, c4d.COLORMODE_RGBf, c4d.PIXELCNT_0)

    # Copy buffer to final picture
    for row in xrange(height):
        # Offset on bitmap row + offset bytes per pixel
        bufferAtOffset = sq.GetOffset(row*(width*inc))

        # Set pixels in bitmap copy
        copy.SetPixelCnt(0, row, width, bufferAtOffset, inc, c4d.COLORMODE_RGBf, c4d.PIXELCNT_0)

    # Show original and copied image in the picture viewer
    c4d.bitmaps.ShowBitmap(orig)
    c4d.bitmaps.ShowBitmap(copy)


if __name__ == '__main__':
    main()