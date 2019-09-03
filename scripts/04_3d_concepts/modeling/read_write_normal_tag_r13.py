"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Reads and Write the Raw Data of a Normal Tag.
    - Normals are stored for each vertex of each polygon.
    - Raw Data normal structure for one polygon is 12 int16 value (4 vectors for each vertex of a Cpolygon * 3 components for each vector) even if the Cpolygon is a Triangle.

Class/method highlighted:
    - c4d.NormalTag
    - c4d.VariableTag.GetLowlevelDataAddressR()
    - c4d.VariableTag.GetLowlevelDataAddressW()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21
"""
import c4d
import array


def CreateNormalTag(op):
    """
     Creates a NormalTag on the passed PolygonObject.

    :param op: The PolygonObject that will received a normal Tag.
    :type op: c4d.PolygonObject
    :return: The created tag.
    :rtype: c4d.NormalTag
    """
    # Checks if the passed object is a polygon object.
    if not isinstance(op, c4d.PolygonObject):
        raise TypeError("op is not a c4d.PolygonObject.")

    # Retrieves the polygonCount
    polyCnt = op.GetPolygonCount()

    # Creates a Normal Tag in memory only
    normalTag = c4d.NormalTag(polyCnt)
    if normalTag is None:
        raise MemoryError("Failed to create a normal Tag.")

    # Inserts the tag to the passed object
    op.InsertTag(normalTag)

    # Notifies the object it need to update to take care of the newly created normal tag
    op.Message(c4d.MSG_UPDATE)
    return normalTag


def ReadNormalTag(tag):
    """
    Read the raw data stored in Normal Tag.

    :param tag: The Normal Tag to read the data from.
    :type tag: c4d.NormalTag
    :return: A list with all the raw data.
    :rtype: list[int]
    """
    # Retrieves the read buffer array
    buffer = tag.GetLowlevelDataAddressR()

    # Converts this BitSeq buffer to a list of short int (int16)
    intArray = array.array('h')
    intArray.fromstring(buffer)
    data = intArray.tolist()

    # Returns the data
    return data


def WriteNormalTag(tag, normalList):
    """
    Write the raw data to a Normal Tag.

    :param tag: The Normal Tag to write the data to.
    :type tag: c4d.NormalTag
    :param normalList: A list with all the raw data.
    :type normalList: list[int]
    """
    # Retrieves the write buffer array
    buffer = tag.GetLowlevelDataAddressW()
    if buffer is None:
        raise RuntimeError("Failed to retrieve internal write data for the normal tag.")

    # Translates list of short int16 to a BitSeq (string are byte in Python 2.7)
    intArray = array.array('h')
    intArray.fromlist(normalList)
    data = intArray.tostring()
    buffer[:len(data)] = data


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Checks if the selected object is a polygon object
    if not isinstance(op, c4d.PolygonObject):
        raise TypeError("op is not a c4d.PolygonObject.")

    # Creates a normal tag
    tag = CreateNormalTag(op)

    # Retrieves the raw data stored into the tag (all values will be equal to 0 since we just created the normal tag)
    rawNormalData = ReadNormalTag(tag)

    # Prints the current value stored in tag, since data are stored as int16 and not float you have to divide them by 32000.0
    print [normal / 32000.0 for normal in rawNormalData]

    # Creates a list representing a float gradient value from 0 to 1 then remap these value from float to int16 by multiplying them by 32000
    valueToSet = [int(float(normalID) / (len(rawNormalData) - 1 ) * 32000.0) for normalID in xrange(len(rawNormalData))]

    # Writes the previous list to the normal tag.
    WriteNormalTag(tag, valueToSet)

    # Reads back the normal stored in the normal tag, value should go from 0 to 1
    print [normal / 32000.0 for normal in ReadNormalTag(tag)]

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()