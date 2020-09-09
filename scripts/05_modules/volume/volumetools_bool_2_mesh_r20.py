"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Converts a Polygon Object to a Volume.
    - Does a boolean operation over two Volume objects.
    - Converts the resulting volume into a Polygon Object.

Class/method highlighted:
    - maxon.Vector
    - maxon.BaseArray
    - maxon.frameworks.volume.VolumeRef
    - maxon.frameworks.volume.VolumeConversionPolygon
    - maxon.frameworks.volume.VolumeToolsInterface.MeshToVolume()
    - maxon.frameworks.volume.VolumeToolsInterface.BoolVolumes()
    - maxon.frameworks.volume.VolumeToolsInterface.VolumeToMesh()

Compatible:
    - Win / Mac
    - R20, R21, S22, R23
"""
import c4d
import maxon
from maxon.frameworks import volume


def polygonToVolume(obj):
    # Checks if the input obj is a PolygonObject
    if not obj.IsInstanceOf(c4d.Opolygon):
        raise TypeError("obj is not a c4d.Opolygon.")

    # Retrieves the world matrices of the object
    matrix = obj.GetMg()

    # Creates a BaseArray (list) of all points position in world space
    vertices = maxon.BaseArray(maxon.Vector)
    vertices.Resize(obj.GetPointCount())
    for i, pt in enumerate(obj.GetAllPoints()):
        vertices[i] = pt * matrix

    # Sets polygons
    polygons = maxon.BaseArray(maxon.frameworks.volume.VolumeConversionPolygon)
    polygons.Resize(obj.GetPolygonCount())
    for i, poly in enumerate(obj.GetAllPolygons()):
        newPoly = maxon.frameworks.volume.VolumeConversionPolygon()
        newPoly.a = poly.a
        newPoly.b = poly.b
        newPoly.c = poly.c

        if poly.IsTriangle():
            newPoly.SetTriangle()
        else:
            newPoly.d = poly.d

        polygons[i] = newPoly

    # Sets the matrix used for local grid translation and rotation
    polygonObjectMatrix = maxon.Matrix()
    polygonObjectMatrix.off = obj.GetMg().off
    polygonObjectMatrix.v1 = obj.GetMg().v1
    polygonObjectMatrix.v2 = obj.GetMg().v2
    polygonObjectMatrix.v3 = obj.GetMg().v3
    gridSize = 1
    bandWidthInterior = 1
    bandWidthExterior = 1
    thread = maxon.ThreadRef()

    volumeRef = None

    # Before R21
    if c4d.GetC4DVersion() < 21000:
        volumeRef = maxon.frameworks.volume.VolumeToolsInterface.MeshToVolume(vertices,
                                                                              polygons, polygonObjectMatrix,
                                                                              gridSize,
                                                                              bandWidthInterior, bandWidthExterior,
                                                                              thread, None)
    else:
        volumeRef = maxon.frameworks.volume.VolumeToolsInterface.MeshToVolume(vertices,
                                                                              polygons, polygonObjectMatrix,
                                                                              gridSize,
                                                                              bandWidthInterior, bandWidthExterior,
                                                                              thread,
                                                                              maxon.POLYGONCONVERSIONFLAGS.NONE, None)
    return volumeRef


def main():
    # Gets the two objects selected and hide them
    objList = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    if not objList:
        raise RuntimeError("Failed to retrieve selected objects, please select two objects.")

    if len(objList) != 2:
        raise RuntimeError("You should select only 2 objects.")

    obj1 = objList[0]
    obj2 = objList[1]
    obj1[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1
    obj2[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 1

    # Checks if the first selected object is a PolygonObject
    if not obj1.IsInstanceOf(c4d.Opolygon):
        raise TypeError("obj1 is not a c4d.Opolygon.")
    # Checks if the second selected object is a PolygonObject
    if not obj2.IsInstanceOf(c4d.Opolygon):
        raise TypeError("obj2 is not a c4d.Opolygon.")

    # Gets a VolumeRef
    vol1 = polygonToVolume(obj1)
    if vol1 is None:
        raise RuntimeError("Failed to convert first obj to volume.")
    vol2 = polygonToVolume(obj2)
    if vol2 is None:
        raise RuntimeError("Failed to convert second obj to volume.")

    # Does the mix operation on the volume
    finalVolume = maxon.frameworks.volume.VolumeToolsInterface.BoolVolumes(vol1, vol2, c4d.BOOLTYPE_DIFF)

    # Converts the volume to object and insert it in the scene
    obj = maxon.frameworks.volume.VolumeToolsInterface.VolumeToMesh(finalVolume, 0, 0.05)
    doc.InsertObject(obj)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
