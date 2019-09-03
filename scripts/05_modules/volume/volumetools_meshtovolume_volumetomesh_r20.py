"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Convert a Polygon Object to a Volume and convert it back to a Polygon Object

Class/method highlighted:
    - Ovolume.SetVolume()
    - maxon.frameworks.volume.VolumeConversionPolygon
    - maxon.frameworks.volume.VolumeToolsInterface.MeshToVolume()
    - maxon.frameworks.volume.VolumeToolsInterface.VolumeToMesh()

Compatible:
    - Win / Mac
    - R20, R21
"""
import c4d
import maxon
from maxon.frameworks import volume


def main():
    # Checks if there is an active object
    if op is None:
        raise ValueError("op is None, please select one object.")

    # Checks if the input obj is a PolygonObject
    if not op.IsInstanceOf(c4d.Opolygon):
        raise TypeError("obj is not a c4d.Opolygon.")

    # Retrieves the world matrices of the object
    matrix = op.GetMg()

    # Creates a BaseArray (list) of all points position in world space
    vertices = maxon.BaseArray(maxon.Vector)
    vertices.Resize(op.GetPointCount())
    for i, pt in enumerate(op.GetAllPoints()):
        vertices[i] = pt * matrix

    # Sets polygons
    polygons = maxon.BaseArray(maxon.frameworks.volume.VolumeConversionPolygon)
    polygons.Resize(op.GetPolygonCount())
    for i, poly in enumerate(op.GetAllPolygons()):
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
    gridSize = 10
    bandWidthInterior = 1
    bandWidthExterior = 1

    # Converts the polygon into a volume
    # Before R21
    if c4d.GetC4DVersion() < 21000:
        volumeRef = maxon.frameworks.volume.VolumeToolsInterface.MeshToVolume(vertices,
                                                                              polygons, polygonObjectMatrix,
                                                                              gridSize,
                                                                              bandWidthInterior, bandWidthExterior,
                                                                              maxon.ThreadRef(), None)
    else:
        volumeRef = maxon.frameworks.volume.VolumeToolsInterface.MeshToVolume(vertices,
                                                                              polygons, polygonObjectMatrix,
                                                                              gridSize,
                                                                              bandWidthInterior, bandWidthExterior,
                                                                              maxon.ThreadRef(),
                                                                              maxon.POLYGONCONVERSIONFLAGS.NONE, None)
    # Creates a Volume Object to store the previous volume calculated
    volumeObj = c4d.BaseObject(c4d.Ovolume)
    if volumeObj is None:
        raise MemoryError("Failed to create a volume object.")

    doc.InsertObject(volumeObj)
    volumeObj.SetVolume(volumeRef)

    # Converts back to Polygon
    polyObject = maxon.frameworks.volume.VolumeToolsInterface.VolumeToMesh(volumeRef, 0.0, 1)
    doc.InsertObject(polyObject)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()