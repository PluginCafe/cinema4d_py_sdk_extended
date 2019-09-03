"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Convert a Polygon Object to a Volume and save this volume to a VDB File
    - Save a VDB file.

Class/method highlighted:
    - maxon.Vector
    - maxon.BaseArray
    - maxon.frameworks.volume.VolumeRef
    - maxon.frameworks.volume.VolumeConversionPolygon
    - maxon.frameworks.volume.VolumeToolsInterface.MeshToVolume()
    - maxon.frameworks.volume.VolumeToolsInterface.SaveVDBFile()

Compatible:
    - Win / Mac
    - R20, R21
"""
import c4d
import maxon
from maxon.frameworks import volume
import os


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
        newpoly = maxon.frameworks.volume.VolumeConversionPolygon()
        newpoly.a = poly.a
        newpoly.b = poly.b
        newpoly.c = poly.c

        if poly.IsTriangle():
            newpoly.SetTriangle()
        else:
            newpoly.d = poly.d

        polygons[i] = newpoly

    polygonObjectMatrix = maxon.Matrix()
    polygonObjectMatrix.off = obj.GetMg().off
    polygonObjectMatrix.v1 = obj.GetMg().v1
    polygonObjectMatrix.v2 = obj.GetMg().v2
    polygonObjectMatrix.v3 = obj.GetMg().v3
    gridSize = 10
    bandWidthInterior = 1
    bandWidthExterior = 1
    thread = maxon.ThreadRef()

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
    # Gets selected objects
    objList = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    if not objList:
        raise RuntimeError("Failed to retrieve selected objects")

    # Creates a maxon.BaseArray with all our obj, we want to convert
    volumesArray = maxon.BaseArray(maxon.frameworks.volume.VolumeRef)
    volumesArray.Resize(len(objList))
    for i, obj in enumerate(objList):
        volumesArray[i] = polygonToVolume(obj)

    try:
        # Generates the final file path to save the vdb
        path = maxon.Url(os.path.join(os.path.dirname(__file__), "file.vdb"))
        scale = 1.0
        metaData = maxon.DataDictionary()
        maxon.frameworks.volume.VolumeToolsInterface.SaveVDBFile(path, scale, volumesArray, metaData)
        print "File saved to ", path
    except Exception as e:
        print "SaveVDBFile error {}, {}".format(e.message, e.args)


if __name__ == '__main__':
    main()