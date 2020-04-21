"""
Copyright: MAXON Computer GmbH
Author: XXX

Description:
    - Writes/Reads simple data to/from memory.

Class/method highlighted:
    - c4d.storage.ByteSeq
    - c4d.storage.MemoryFileStruct
    - c4d.storage.HyperFile

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22
"""
import c4d


def WriteMemoryFile():
    """
    Writes data to a memory file.

    :return: The byte sequence or None
    """
    # Creates a MemoryFile, data will be written in
    mfs = c4d.storage.MemoryFileStruct()

    # Sets the memory file ready to be written to
    mfs.SetMemoryWriteMode()

    # Initializes a HyperFile
    file = c4d.storage.HyperFile()

    # Opens the HyperFile, with the MemoryFile used
    if not file.Open(0, mfs, c4d.FILEOPEN_WRITE, c4d.FILEDIALOG_NONE):
        raise RuntimeError("Failed to open the HyperFile.")

    # Writes a string to the memory file
    file.WriteString("MemoryFileStruct Example")

    # Writes an integer to the memory file
    file.WriteLong(1214)

    # Closes the file
    file.Close()

    # Returns the memory file data (the byte sequence)
    return mfs.GetData()[0]


def ReadMemoryFile(data):
    """
    Reads data from a memory file.

    :param data: the byte sequence to read
    """
    # Creates a MemoryFile, data will be read in
    mfs = c4d.storage.MemoryFileStruct()

    # Sets the memory file ready to be read from
    mfs.SetMemoryReadMode(data, len(data))

    file = c4d.storage.HyperFile()
    # Opens the memory file and set it ready for reading
    if not file.Open(0, mfs, c4d.FILEOPEN_READ, c4d.FILEDIALOG_NONE):
        raise RuntimeError("Failed to open the HyperFile.")

    # Reads the string from the memory file
    value = file.ReadString()
    print("The string value is :", value)

    # Reads the int from the memory file
    value = file.ReadLong()
    print("The int value is :", value)

    # Closes file
    file.Close()


def main():
    # Write data in a MemoryFile and get the byte sequence
    bytes = WriteMemoryFile()

    # Read data from the byte sequence
    ReadMemoryFile(bytes)


if __name__ == '__main__':
    main()
