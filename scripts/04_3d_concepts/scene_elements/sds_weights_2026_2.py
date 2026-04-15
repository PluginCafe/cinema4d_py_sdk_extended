
"""Demonstrates how to read and write data of an SDS weight tag.
"""
__author__: str = "Ferdinand Hoppe"
__copyright__: str = "Copyright (C) 2026 MAXON Computer GmbH"
__date__: str = "02/09/2026"
__license__: str = "Apache-2.0 License"
__version__: str = "2026.2.0"

from mxutils import CheckType

import c4d
import pprint

op: c4d.BaseObject | None  # The currently active object.
doc: c4d.documents.BaseDocument  # The currently active document.

def CreateSdsSetup(name: str = "") -> c4d.BaseTag:
    """Creates a simple SDS setup with a cube polygon child and an SDS weight tag, and returns the 
    weight tag.

    Not relevant for the example, and therefore abstracted into a function.
    """
    # Construct a cube polygon object and set its geometry.
    polyCube: c4d.PolygonObject = CheckType(c4d.PolygonObject(8, 6))
    polyCube.SetName(name)
    points: list[c4d.Vector] = [
        c4d.Vector(-50, -50, -50), c4d.Vector(50, -50, -50), 
        c4d.Vector(50, 50, -50), c4d.Vector(-50, 50, -50),
        c4d.Vector(-50, -50, 50), c4d.Vector(50, -50, 50), 
        c4d.Vector(50, 50, 50), c4d.Vector(-50, 50, 50)
    ]
    polyCube.SetAllPoints(points)

    polygons: list[c4d.CPolygon] = [
        c4d.CPolygon(0, 1, 2, 3), c4d.CPolygon(5, 4, 7, 6), c4d.CPolygon(4, 0, 3, 7),
        c4d.CPolygon(1, 5, 6, 2), c4d.CPolygon(3, 2, 6, 7), c4d.CPolygon(4, 5, 1, 0)
    ]
    for i, poly in enumerate(polygons):
        polyCube.SetPolygon(i, poly)

    # Create the SDS object and parent the cube under it.
    sdsObject: c4d.BaseObject = CheckType(c4d.BaseObject(c4d.Osds))
    sdsObject[c4d.SDSOBJECT_SUBEDITOR_CM] = 4
    sdsObject[c4d.SDSOBJECT_SUBRAY_CM] = 4

    sdsObject.SetName(f"SDS - {name}")
    polyCube.InsertUnder(sdsObject)
    doc.InsertObject(sdsObject)

    # Add the SDS weight tag to the polygon object.
    phongTag: c4d.BaseTag = CheckType(sdsObject.MakeTag(c4d.Tphong))
    weightTag: c4d.BaseTag = CheckType(polyCube.MakeTag(c4d.Tsds))
    polyCube.Message(c4d.MSG_UPDATE)
    doc.ExecutePasses(None, True, True, True, c4d.BUILDFLAGS_NONE)
    c4d.EventAdd()

    return weightTag

def CloneSdsSetup(tag: c4d.BaseTag, name: str) -> c4d.BaseTag:
    """Clones the SDS setup of the given SDS object and returns the weight tag of the cloned setup.

    Not relevant for the example, and therefore abstracted into a function.
    """
    if not isinstance(tag, c4d.BaseTag) or tag.GetType() != c4d.Tsds:
        raise TypeError("The provided tag must be an SDS weight tag.")
    
    # Get the object of the tag and go up one level when the parent of the object is an SDS object.
    # Not really an exact science but makes sense for most SDS setups.
    host: c4d.BaseObject = tag.GetObject()
    if host.GetUp() and host.GetUp().GetType() == c4d.Osds:
        host = host.GetUp()

    # Clone the host object, update its name and position, and insert it into the document.
    clone: c4d.BaseObject = CheckType(host.GetClone(c4d.COPYFLAGS_NONE))
    clone.SetName(f"SDS - {name}")
    clone.SetMg(host.GetMg() * c4d.utils.MatrixMove(c4d.Vector(150, 0, 0)))
    host.GetDocument().InsertObject(clone)

    # Get the weight tag from the cloned setup and return it.
    tag: c4d.BaseTag = (CheckType(clone.GetDown().GetTag(c4d.Tsds)) 
                        if clone.GetType() == c4d.Osds else 
                        CheckType(clone.GetTag(c4d.Tsds)))
    return tag


def main() -> None:
    """Called by Cinema 4D when the script is being executed.
    """
    # Get the SDS tag from the active object or create a new setup when there is no active object
    # or no SDS tag on the active object.
    c4d.ClearPythonConsole()
    sdsTag: c4d.BaseTag | None = op.GetTag(c4d.Tsds) if op else None
    if sdsTag is None:
        sdsTag = CreateSdsSetup("Point Weights")

    # Initialize the tag (important to do this before accessing tag data) and get its data.
    sdsTag.InitFromObject()
    sdsData: dict = sdsTag.GetTagData()
    print("Initial tag data:")
    pprint.pprint(sdsData)

    # {'points': 8,
    # 'pointweight': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    # 'polys': 6,
    # 'polyweight': [ {'a': 0.0, 'b': 0.0, 'c': 0.0, 'd': 0.0},
    #                 {'a': 0.0, 'b': 0.0, 'c': 0.0, 'd': 0.0},
    #                 {'a': 0.0, 'b': 0.0, 'c': 0.0, 'd': 0.0},
    #                 {'a': 0.0, 'b': 0.0, 'c': 0.0, 'd': 0.0},
    #                 {'a': 0.0, 'b': 0.0, 'c': 0.0, 'd': 0.0},
    #                 {'a': 0.0, 'b': 0.0, 'c': 0.0, 'd': 0.0}]

    # Now lets write all point weights at one by setting them to a gradient from 0.0 to 1.0. Here
    # we write a weight for each vertex of the the object, eight when we are using the cube from 
    # this example.
    pointCount: int = sdsData.get("points", 0)
    pointWeights: list[float] = [c4d.utils.RangeMap(
        i, 0, pointCount - 1, 0.0, 1.0, True) for i in range(pointCount)]
    sdsTag.SetAllPointWeights(pointWeights)

    # We can also set point weights individually, for example to set the first vertex to 0.5:
    sdsTag.SetPointWeight(0, 0.5)

    # Now let's clone the object and do the same for edge weights.
    otherTag: c4d.BaseTag = CloneSdsSetup(sdsTag, "Edge Weights")
    otherTag.InitFromObject()

    sdsData: dict = otherTag.GetTagData()
    polyCount: int = sdsData.get("polys", 0)
    f: float = 1 / polyCount 

    # Set again all weights at once. But due to how edges work, this can lead to funky results,
    # as each edge could be shared by up to two polygons, and when we set the weight X for
    # edge a of polygon 0 and the weight Y for edge b of polygon 1 (and a and b are actually the
    # same edge), the competing weights must be normalized.
    polyWeights: list[dict[str, float]] = [
        {'a': i * f, 'b': i * f, 'c': i * f, 'd': i * f} for i in range(polyCount)
    ]
    # otherTag.SetAllPolyWeights(polyWeights)

    # It is more sensible to set weights for edges individually. Note that for triangles, we have to
    # set A, B, and D. I.e., it deviates from how triangles are stored themselves in a CPolygon,
    # where A, B, C, are used and D is just a duplicate of C.
    pid: int = 0 # The polygon index we want to set edge weights for.
    for edgeIdx in range(4):
        weight: float = 1.0
        otherTag.SetPolyEdgeWeight(pid, edgeIdx, weight, validate=True)
    
    c4d.EventAdd()

if __name__ == '__main__':
    main()