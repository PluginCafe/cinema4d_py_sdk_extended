"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam, Ferdinand Hoppe

Description:
    - Script creates a NormalTag for a selected polygon object with a phong
      tag where the normals have been rotated by 45° around the world z-axis.
    - Showcases read and write operations for the normals of a NormalTag.
    - Normals are stored for each vertex of each polygon.
    - Raw data normal structure for one polygon is 12 int16 value (4 vectors 
      for each vertex of a Cpolygon * 3 components for each vector), even if 
      the Cpolygon is a triangle.

Class/method highlighted:
    - c4d.NormalTag
    - c4d.VariableTag.GetLowlevelDataAddressR()
    - c4d.VariableTag.GetLowlevelDataAddressW()

"""
import c4d
import array
import math

QUARTER_PI = math.pi * .25

def ReadNormalTag(tag):
    """Reads a c4d.NormalTag to a list of c4d.Vector.

    Args:
        tag (c4d.NormalTag): The tag to read the normals from.

    Returns:
        list[c4d.Vector]: The read normals. There are polygon_count * 4 normals, i.e. each vertex has a normal for each polygon it is attached to.

    Raises:
        TypeError: When tag is not a c4d.NormalTag.
        RuntimeError: When the memory of the tag cannot be read.
    """
    if not (isinstance(tag, c4d.BaseTag) and tag.CheckType(c4d.Tnormal)):
        msg = f"Expected normal tag, received: {tag}."
        raise TypeError(msg)

    # Get the read-only normal tag buffer.
    buffer = tag.GetLowlevelDataAddressR()
    if buffer is None:
        msg = "Failed to retrieve memory buffer for VariableTag."
        raise RuntimeError(msg)

    # Init an int16 array with the raw buffer. For details on Python's typed 
    # arrays see:
    #   https://docs.python.org/3.7/library/array.html
    data = array.array('h')
    data.frombytes(buffer)

    # Convert the int16 representation of the normals to a list of c4d.Vector.
    factor = 1 / 32000.0
    return [c4d.Vector(data[i-3] * factor,
                       data[i-2] * factor,
                       data[i-1] * factor)
            for i in range(3, len(data) + 3, 3)]

def WriteNormalTag(tag, normals, doNormalize=True):
    """Writes a list of c4d.Vector to a c4d.NormalTag.
    
    Does not ensure that normals is only composed of c4d.Vector.

    Args:
        tag (c4d.NormalTag): The tag to write the normals into.
        normals (list[c4d.Vector]): The normals to write.
        doNormalize (bool, optional): If True, the input normals will be normalized. If False, they will not.. Defaults to True.

    Raises:
        TypeError: When tag is not a c4d.NormalTag.
        RuntimeError: When the memory of the tag cannot be read.
        IndexError: When normals does not match the size of tag.
    """
    if not (isinstance(tag, c4d.BaseTag) and tag.CheckType(c4d.Tnormal)):
        msg = f"Expected normal tag, received: {tag}."
        raise TypeError(msg)

    # Get the writable normal tag buffer.
    buffer = tag.GetLowlevelDataAddressW()
    if buffer is None:
        msg = "Failed to retrieve memory buffer for VariableTag."
        raise RuntimeError(msg)

    # Normalize the input if requested.
    if doNormalize:
        normals = [n.GetNormalized() for n in normals]

    # Convert c4d.Vector normals to int16 representation.
    raw_normals = [int(component * 32000.0)
                   for n in normals for component in (n.x, n.y, n.z)]

    # Catch input data of invalid length.
    count = tag.GetDataCount()
    if count * 12 != len(raw_normals):
        msg = (f"Invalid data size. Expected length of {count}. "
               f"Received: {len(raw_normals)}")
        raise IndexError(msg)

    # Write the data back. For details on Python's typed arrays, see:
    #   https://docs.python.org/3.7/library/array.html
    data = array.array('h')
    data.fromlist(raw_normals)
    data = data.tobytes()
    buffer[:len(data)] = data

def main():
    """Entry point."""
    # Raise an error when the primary selection is not a PolygonObject.
    if not isinstance(op, c4d.PolygonObject):
        raise ValueError("Please select a PolygonObject.")

    # Attempt to get the phong tag of the object.
    if op.GetTag(c4d.Tphong) is None:
        raise ValueError("Selected object does not carry a phong tag.")

    # Get the phong normals of the phong tag of the object and rotate them
    # all by 45° around the global z-axis.
    phongNormals = [nrm * c4d.utils.MatrixRotZ(QUARTER_PI) 
                    for nrm in op.CreatePhongNormals()]

    # Create a new NormalTag with a size of the polygon count of our object.
    normalTag = c4d.NormalTag(count=op.GetPolygonCount())
    if normalTag is None:
        raise MemoryError("Failed to create a NormalTag.")

    # Get the normals from the newly allocated NormalTag.
    normals = ReadNormalTag(normalTag)
    print (f"Normals of the newly allocated tag: {normals}")

    # This should not happen.
    if len(phongNormals) != len(normals):
        raise RuntimeError("Unexpected NormalTag to phong normals mismatch.")

    # Write the phong normals into our NormalTag.
    WriteNormalTag(normalTag, phongNormals)

    # Inspect our write operation in the console.
    normals = ReadNormalTag(normalTag)
    print (f"Normals after writing the phong normals: {normals}")

    # Start an undo block.
    doc.StartUndo()
    # Insert our NormalTag.
    op.InsertTag(normalTag)
    # For insertions the undo has to be added after the operation.
    doc.AddUndo(c4d.UNDOTYPE_NEW, normalTag)
    # End the undo block.
    doc.EndUndo()

    # Notify Cinema and the object that we did made changes.
    op.Message(c4d.MSG_UPDATE)
    c4d.EventAdd()

if __name__ == "__main__":
    main()
