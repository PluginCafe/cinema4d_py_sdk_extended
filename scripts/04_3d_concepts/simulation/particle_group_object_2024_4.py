"""Demonstrates how to read particle data from a ParticleGroupObject.

This script is not about the legacy particle system, but the new particle system introduced in 
Cinema 4D 2024.4. The script demonstrates read access to particle data from a ParticleGroupObject.
It is currently not possible to persistently write data back to the particle system. If you want
to feed data back into the particle system, you should generate meshes or splines which can be
used as emitter geometry for the particle system.

To run this script, create a new particle emitter object in the scene, select the also created new
particle group object, press play to simulate the particles, and then run the script. The script 
will print selected particle data and create null objects representing these particles in the scene.

Note:
    - The method ParticleGroupObject.GetAttributeChannelData() is currently bugged for the color and 
      alignment channels. We must use here the specialized functions GetParticleColorsR and
      GetParticleAlignmentsR. This will be fixed in a future version of Cinema 4D.
    - The setter c4d.Quaternion.v is currently bugged. This will be fixed in a future version of
      Cinema 4D. But this makes it currently impossible to construct a c4d.Quaternion from the
      maxon::Quaternion32 data exposed by the particle system. As a workaround, we can construct
      a particle alignment from the particle velocity.

See Also:
    - Python Software Foundation (2024). struct module: Formatting Characters. 
      url: https://docs.python.org/3/library/struct.html#format-characters
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2024 MAXON Computer GmbH"
__date__ = "08/04/2024"
__license__ = "Apache-2.0 License"
__version__ = "2024.4"

import c4d
import pprint
import struct
import mxutils

doc: c4d.documents.BaseDocument  # The currently active document.
op: c4d.BaseObject | None # The primary selected object in `doc`. Can be `None`.


def GetParticleInfo(op: c4d.ParticleGroupObject, channel: str) -> dict:
    """Demonstrates how to access storage conventions for the channel of a particle group.

    Doing this is necessary to correctly unpack the data from a particle group channel buffer. Find
    below a list of the currently existing channels (as of 2024.4) and their associated element 
    size, stride, and data type. Note that this list might be subject to change in future versions 
    of Cinema 4D and this list might then be incomplete or outdated. Always check the data with 
    ParticleGroupObject.GetAttributeChannelDescriptions() yourself when in doubt.

      Name                                            Size       Stride    Type
    ------------------------------------------------------------------------------------------------
    - net.maxon.particles.attribute.uniqueid          (4 bytes,   4 bytes, uint32)
    - net.maxon.particles.attribute.positions         (24 bytes, 24 bytes, vec<3,float32> or
                                                                           vec<3,float64>)
    - net.maxon.particles.attribute.velocity          (12 bytes, 16 bytes, vec<3,float32>)
    - net.maxon.particles.attribute.color             (16 bytes, 16 bytes, col<4,float32>)
    - net.maxon.particles.attribute.age               ( 4 bytes,  4 bytes, float32)
    - net.maxon.particles.attribute.lifetime          ( 4 bytes,  4 bytes, float32)
    - net.maxon.particles.attribute.radius            ( 4 bytes,  4 bytes, float32)
    - net.maxon.particles.attribute.distancetraversed ( 4 bytes,  4 bytes, float32)
    - net.maxon.particles.attribute.uniqueid          ( 4 bytes,  4 bytes, uint32)
    - net.maxon.particles.attribute.alignments        (16 bytes, 16 bytes, Quaternion32)
    - net.maxon.particles.attribute.angularvelocity   (12 bytes, 16 bytes, vec<3,float32>)
    """
    # Get the particle data descriptions, they hold information about how each channel for this
    # particle group is stored in memory.
    descriptions: list[dict] = op.GetAttributeChannelDescriptions()

    # pprint.pprint(descriptions)
    #
    # [{"Data Size in bytes": 4,                           # The size of each element in bytes.
    #   "Data Stride in bytes": 4,                         # The width an element is given in
    #                                                        the buffer, not all channels pack their
    #                                                        elements tightly.
    #   "Data Type": "unsigned int32",                     # The data type which is being packed.
    #   "Name": "net.maxon.particles.attribute.uniqueid"}, # The name of the channel.
    #
    #  {"Data Size in bytes": 24,
    #   ...

    descriptions: dict[str, dict] = {d["Name"]: d for d in descriptions}
    if channel not in descriptions.keys():
        raise ValueError(
            f"The channel '{channel}' does not exist for the particle group {op}.")
    return descriptions[channel]


def GetParticleAges(op: c4d.ParticleGroupObject) -> list[float]:
    """Unpacks the particle ages.

    Provides a basic insight into how to unpack particle data from a particle group object.
    """
    # Get the data buffer for the readable age channel, i.e., we can only read data from this
    # buffer. There is also a writable buffer, but it has limited usage, as all write operations
    # are volatile, i.e., are lost the next time the simulation is being updated.
    ageBuffer: memoryview = op.GetParticleAgesR()
    ageWriteBuffer: memoryview = op.GetParticleAgesW()

    # There are many more of these specialized functions to get buffers for particle data, but since
    # we often must validate the structure of that data, and therefore have to know the chanel name,
    # we can just use the generic `GetParticleInfo` function to get the information we need. But
    # this buffer is always readonly.
    ageBuffer: memoryview = op.GetAttributeChannelData("net.maxon.particles.attribute.age")
    if ageBuffer is None:
        return []

    # Get the channel information for the age channel.
    info: dict = GetParticleInfo(op, "net.maxon.particles.attribute.age")

    # Unpack the age data from the buffer into a list of floats. The stride is the distance between
    # each element in the buffer, and the size is the size of each element in the buffer. They do
    # not have to be same, as the buffer might have padding between elements. We do not need the
    # size value as it is explicitly expressed by the character "f" in the unpack_from function.
    size: int = info["Data Size in bytes"]
    stride: int = info["Data Stride in bytes"]
    return [struct.unpack_from("f", ageBuffer, i)[0] for i in range(0, len(ageBuffer), stride)]


def GetParticleVelocities(op: c4d.ParticleGroupObject) -> list[c4d.Vector]:
    """Unpacks the particle velocities.

    The velocities are stored as triples of floats, Vec3<float32>, we unpack them here in groups of
    three floats ("fff") into a singular vector.
    """
    velBuffer: memoryview = op.GetAttributeChannelData("net.maxon.particles.attribute.velocity")
    if velBuffer is None:
        return []

    info: dict = GetParticleInfo(op, "net.maxon.particles.attribute.velocity")
    stride: int = info["Data Stride in bytes"]

    # Unpack the velocity data from the buffer into a list of c4d.Vector instances. Because the
    # velocities are stored as triples of floats, Vec3<float32>, we unpack them here in groups of
    # three floats ("fff") into a singular vector.
    return [c4d.Vector(*struct.unpack_from("fff", velBuffer, i))
            for i in range(0, len(velBuffer), stride)]


def GetParticlePositions(op: c4d.ParticleGroupObject) -> list[c4d.Vector]:
    """Unpacks the particle positions. 

    The special case here is that the positions can be stored as either 32bit or 64bit vectors, so 
    we have to select our unpacking character accordingly.
    """
    posBuffer: memoryview = op.GetAttributeChannelData("net.maxon.particles.attribute.positions")
    if posBuffer is None:
        return []

    info: dict = GetParticleInfo(op, "net.maxon.particles.attribute.positions")
    stride: int = info["Data Stride in bytes"]
    size: int = info["Data Size in bytes"]
    format: str = "fff" if size == 12 else "ddd"

    return [c4d.Vector(*struct.unpack_from(format, posBuffer, i))
            for i in range(0, len(posBuffer), stride)]


def GetParticleColors(op: c4d.ParticleGroupObject) -> list[c4d.Vector4d]:
    """Unpacks the particle colors. 

    More of the same, but here we have a four component vector.
    """
    # GetAttributeChannelData is currently bugged for the color channel, we must use the specialized
    # function here for now.

    # colBuffer: memoryview = op.GetAttributeChannelData("net.maxon.particles.attribute.color")
    colBuffer: memoryview = op.GetParticleColorsR()
    if colBuffer is None:
        return []

    info: dict = GetParticleInfo(op, "net.maxon.particles.attribute.color")
    stride: int = info["Data Stride in bytes"]

    return [c4d.Vector4d(*struct.unpack_from("ffff", colBuffer, i))
            for i in range(0, len(colBuffer), stride)]


def GetParticleAlignments(op: c4d.ParticleGroupObject) -> list[tuple]:
    """Unpacks the particle alignments. 

    The alignments are expressed as maxon.Quaternion32. Note that this type is NOT identical to
    c4d.Quaternion.
    """
    # GetAttributeChannelData is currently bugged for the alignment channel, we must use the
    # specialized function here for now.

    # alignBuffer: memoryview = op.GetAttributeChannelData("net.maxon.particles.attribute.alignments")
    alignBuffer: memoryview = op.GetParticleAlignmentsR()
    if alignBuffer is None:
        return []

    info: dict = GetParticleInfo(op, "net.maxon.particles.attribute.alignments")
    stride: int = info["Data Stride in bytes"]

    # Unpack the quaternion data from the buffer into a list of quadruples. It is currently not
    # possible to construct a c4d.Quaternion from the data, as Quaternion.v is currently bugged.
    # This will be fixed in a future version of Cinema 4D.
    quaternions: list[tuple] = []
    for i in range(0, len(alignBuffer), stride):
        x, y, z, w = struct.unpack_from("ffff", alignBuffer, i)
        quaternions.append((x, y, z, w))

        # In a future version of Cinema 4D, the following code will work. SetAxis cannot be used to
        # set Quaternion.v, and .w directly.
        # quat: c4d.Quaternion = c4d.Quaternion()
        # quat.v = c4d.Vector(x, y, z)
        # quat.w = w
        # quaternions.append(quat)

    return quaternions


def main() -> None:
    """Called by Cinema 4D when the script is being executed.
    """
    if not isinstance(op, c4d.ParticleGroupObject):
        raise ValueError("The selected object is not a ParticleGroupObject.")

    # Get and print the particle data for the first five particles.
    ages: list[float] = GetParticleAges(op)
    print("\nParticle ages:")
    pprint.pprint(ages[:5 if len(ages) >= 5 else len(ages)])

    positions: list[c4d.Vector] = GetParticlePositions(op)
    print("\nParticle positions:")
    pprint.pprint(positions[:5 if len(positions) >= 5 else len(positions)])

    velocities: list[c4d.Vector] = GetParticleVelocities(op)
    print("\nParticle velocities:")
    pprint.pprint(velocities[:5 if len(velocities) >= 5 else len(velocities)])

    colors: list[c4d.Vector] = GetParticleColors(op)
    print("\nParticle colors:")
    pprint.pprint(colors[:5 if len(colors) >= 5 else len(colors)])

    alignments: list[c4d.Quaternion] = GetParticleAlignments(op)
    print("\nParticle alignments:")
    pprint.pprint(alignments[:5 if len(alignments) >= 5 else len(alignments)])

    if not positions or not velocities:
        return

    # Construct global transforms for the first five particles and insert null objects for them. See
    # Python API Matrix manual for details of how to construct a matrix from a position and a vector.
    # It is currently not possible to construct frames for the "true" alignments of particles, as
    # the Quaternion.v property is bugged. This will be fixed in a future version of Cinema 4D. This
    # approach is flawed as constructing a frame from one vector lacks information for one of the
    # three degrees of freedom. The chosen up vector will impact the banking of particles.

    transforms: list[tuple[c4d.Vector, c4d.Vector]] = list(zip(positions, velocities))
    length: int = 5 if len(transforms) >= 5 else len(transforms)
    eps: float = 1E-5

    # Iterate over the position-velocity pairs for the first five particles.
    for i, (pos, vel) in enumerate(transforms[:length]):

        # Construct a frame in global space from the position and velocity data. The particle data
        # is expressed in global space.
        up: c4d.Vector = c4d.Vector(0, 1, 0)
        up = up if 1. - abs(vel * up) > eps else c4d.Vector(eps, 1, 0)
        z: c4d.Vector = vel.GetNormalized()
        temp: c4d.Vector = z.Cross(up)
        y: c4d.Vector = z.Cross(temp).GetNormalized()
        x: c4d.Vector = y.Cross(z).GetNormalized()

        # Construct a global matrix from the position and our frame.
        matrix: c4d.Matrix = c4d.Matrix(off=pos, v1=x, v2=y, v3=z)

        # Insert a null object that represents the particle.
        null: c4d.BaseObject = mxutils.CheckType(c4d.BaseObject(c4d.Onull))
        null[c4d.NULLOBJECT_DISPLAY] = c4d.NULLOBJECT_DISPLAY_AXIS
        null.SetMg(matrix)
        doc.InsertObject(null)

    c4d.EventAdd()  # Update the Cinema 4D scene.


if __name__ == "__main__":
    main()
