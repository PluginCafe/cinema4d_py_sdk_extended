"""
Copyright: MAXON Computer GmbH

Description:
    - Writes/Reads a bitmap to/from memory.

Class/method highlighted:
    - c4d.storage.ByteSeq
    - c4d.storage.MemoryFileStruct
    - c4d.storage.HyperFile
    - HyperFile.WriteImage()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22
"""
import c4d


def WriteBitmap(bmp, format=c4d.FILTER_B3D, settings=c4d.BaseContainer()):
    """
    Write an hyper file image to a buffer object.

    :param bmp: The image to convert into a buffer object
    :param format: The filter type
    :param settings: Optional settings
    :return:The byte sequence or None
    """

    # Creates a MemoryFile, data will be written in
    mfs = c4d.storage.MemoryFileStruct()
    mfs.SetMemoryWriteMode()

    # Initializes a HyperFile
    hf = c4d.storage.HyperFile()

    # Opens the HyperFile, with the MemoryFile used
    if not hf.Open(0, mfs, c4d.FILEOPEN_WRITE, c4d.FILEDIALOG_NONE):
        raise RuntimeError("Failed to open the HyperFile.")

    # Writes the bitmap
    if not hf.WriteImage(bmp, format, settings):
        raise RuntimeError("Failed to write image in the HyperFile.")

    # Closes the HyperFile, data are now in our MemoryFile
    hf.Close()

    # Returns the data stored in the MemoryFile
    byteseq, size = mfs.GetData()
    return byteseq, size


def ReadBitmap(byteseq):
    """
    Creates a bitmap from a buffer object.

    :param byteseq: The buffer object.
    :return: The image if succeeded, otherwise False
    """
    # Initializes our HyperFile, MemoryFile and bmp where data will be stored
    hf = c4d.storage.HyperFile()
    mfs = c4d.storage.MemoryFileStruct()
    bmp = None

    # Defines the memory address to read, and the size of this block
    mfs.SetMemoryReadMode(byteseq, len(byteseq))

    # Opens the hyperfile, with the MemoryFile used
    if not hf.Open(0, mfs, c4d.FILEOPEN_READ, c4d.FILEDIALOG_NONE):
        raise RuntimeError("Failed to open the HyperFile.")

    # Reads the bitmap
    bmp = hf.ReadImage()

    # Closes the HyperFile
    hf.Close()

    return bmp


def main():
    # Opens a Dialog to choose a picture file
    path = c4d.storage.LoadDialog(type=c4d.FILESELECTTYPE_IMAGES, title="Please Choose an Image:")
    if not path:
        return

    # Creates and initialize selected image
    img = c4d.bitmaps.BaseBitmap()
    if img is None:
        raise RuntimeError("Failed to create a BaseBitmap.")

    # If initialization went wrong, display an error
    if img.InitWith(path)[0] != c4d.IMAGERESULT_OK:
        raise RuntimeError("Cannot load image \"" + path + "\".")

    # Saves BaseBitmap with a HyperFile and retrieve the byte sequence
    byteseq, size = WriteBitmap(img)

    # Reads BaseBitmap from the byte sequence
    bmp = ReadBitmap(byteseq)

    # Displays the bitmap in the Picture Viewer
    c4d.bitmaps.ShowBitmap(bmp)


if __name__ == '__main__':
    main()
