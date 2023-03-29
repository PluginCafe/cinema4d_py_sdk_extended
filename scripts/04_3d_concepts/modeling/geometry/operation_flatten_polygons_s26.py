#coding: utf-8
"""Demonstrates how to deform points of a point object at the example of 'flattening' the selected
polygons in a polygon object.

'Flattening' means here projecting all point which are part of the active polygon selection into
the mean plane of that polygon selection. The example will either project the selected polygons of 
the selected PolygonObject instance, or, when no object selection is present, generate an example 
geometry for which then the polygon selection will be flattened.

Note:
    See the modelling_smc_flatten example when interested in flattening points, edges, or polygons
    with the Flatten tool in a convenient manner. This example is not about the Flatten tool but 
    about how such tool can be implemented.

Topics:
    * Implementing a point deformation operation
    * Orthogonally projecting points into a plane
    * Evaluating the normals of polygons and vertices
    * Polygon selections
    * c4d.PolygonObject
    * c4d.CPolygon

Examples:
    * ProjectIntoPlane(): Projects #p orthogonally into the plane defined by #q and #normal.
    * GetPolygonNormal(): Returns the normal of the polygon defined by the passed points.
    * FlattenPolygonObjectSelection(): Projects the selected polygons in #node into the mean plane 
     of the selection.

Overview:
    Other than modelling tools which construct geometry, tools which just deform point objects are 
    often less critical regarding updating adjacent data of the object and also easier to implement
    in general. Less 'adjacent' data of a point object is affected by simple point transformations, 
    e.g., a UVW tag will still be valid. But a NormalTag for example will be invalidated by a point
    deformation of the PolygonObject it has been built for. Just as for modelling operations which 
    construct geometry, it is therefore recommended to instead use SendModelingCommand() wherever 
    possible. This file serves as a simple example for how such tool works which deforms the points
    of a geometry.
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2022 MAXON Computer GmbH"
__date__ = "08/04/2022"
__license__ = "Apache-2.0 License"
__version__ = "S26"

import c4d
import typing

doc: c4d.documents.BaseDocument  # The currently active document.
op: typing.Optional[c4d.BaseObject]  # The selected object within that active document. Can be None.


def AssertType(item: any, t: typing.Type) -> None:
    """Asserts the type of #item.
    """
    if not isinstance(item, t):
        raise TypeError(f"Expected {t} for {item}.")


def GetMean(collection: typing.Collection) -> typing.Any:
    """Returns the arithmetic mean of #collection. 

    Args:
        collection: An iterable of types that support addition operations between each other, where
         the sum of them supports multiplication.

    Returns:
        The arithmetic mean of #collection.
    """
    return sum(collection) * (1. / len(collection))


def ProjectIntoPlane(p: c4d.Vector, q: c4d.Vector, normal: c4d.Vector) -> c4d.Vector:
    """Projects the point #p orthogonally into the plane defined by #q and #normal.

    Args:
        p: The point to project.
        q: A point in the plane.
        normal: The normal of the plane (expected to be a normalized vector).

    Returns:
        The projected point.
    """
    AssertType(p, c4d.Vector)
    AssertType(q, c4d.Vector)
    AssertType(normal, c4d.Vector)

    # The distance from the point #p to its orthogonal projection #p' on the plane. Or, in short,
    # the length of the shortest path (in euclidean space) from #p to the plane.
    distance = (p - q) * normal
    # Calculate #p' by moving #p #distance units along the inverse plane normal.
    return p - normal * distance


def GetPolygonNormal(points: typing.Collection[c4d.Vector]) -> c4d.Vector:
    """Returns the normal of the polygon defined by the passed points.

    Cinema 4D provides normals for polygon objects in the form of normal and phong tags. Both forms
    of normal storage are not always accessible, as these tags are not always present on an object.
    Both tags usually also store interpolated normals which most of the time are undesirable for
    modelling operations. This function demonstrates how to compute the raw normal of a polygon and
    its vertices. There are more performant ways to compute these normals, but this example has been
    written with clarity of operations and not with efficiency in mind.

    The normal #ni of the i-th vertex #i in a polygon is defined by the normalized cross product 
    of its edges #e1 and #e2. #e1 is the edge connecting #i to the previous vertex #h in the 
    polygon, and #e2 the edge connecting #i to the next vertex #j.

        Quadrangle              Triangle      

        * ----- j                     j      
        |       |                   / |      
        |    ni | e2              / ni| e2       
        |      \|               /    \|       
        h -----[i]             h ----[i]      
            e1                    e1            

        e1 = (h - i)
        e2 = (i - j)
        ni = normalize(e1 x e2)

    The normal #n of a polygon #P is then the arithmetic mean of all its vertex normals.

       nd      nb
        \       \    
         d ----- c   
         |  n    |   
       na|   \ nb|    <---   Polygon P
        \|      \|   
         a ----- b      

        Triangle:

            na + nb + nc
        n = ------------
                 3

        Quadrangle:

            na + nb + nc + nd
        n = -----------------
                    4      

    To be more efficient in computation, one should at least leave out the step of normalizing all
    vertex normals and instead just normalize the final polygon normal when the vertex normals are
    not required as an output. Normalization is an expensive operation since it entails calculating 
    the length of a vector. In practice, floating precision errors would so require one to normalize 
    the polygon normal when the vertex normals had been normalized. 

        vertexNormals = []
        for h, i, j in vertexNeighborhoodTriples:
            vertexNormals.append((h - i) x (j - i))

        n = normalize(mean(vertexNormals))

    Args:
        points: The points of a polygon in consecutive order. Can either be three or four points.
    """
    # Assert the inputs.
    AssertType(points, (list, tuple))
    if len(points) not in (3, 4):
        raise RuntimeError(f"Invalid length for: {points}")

    count = len(points)
    vertexNormals = []

    # Iterate over all points.
    for index in range(count):
        # Determine the current vertex #i and its two neighbors #h and #j. For the first and last
        # point, the neighborhood lookup must loop over.
        h = points[index - 1] if index > 0 else points[count - 1]
        i = points[index]
        j = points[index + 1] if index < (count - 1) else points[0]
        # Compute the cross product for the two edges of the vertex.
        e1, e2 = (h - i), (i - j)
        vertexNormals.append(e1 % e2)

    # Return normalized mean of #vertexNormals. The operator ~ carries out normalization for the
    # type c4d.Vector.
    return ~GetMean(vertexNormals)


def FlattenPolygonObjectSelection(node: c4d.PolygonObject, strength: float) -> c4d.PolygonObject:
    """Projects the selected polygons in #node into the mean plane of the selection.

    Args:
        strength: The strength value in the interval [0, 1] with which the projection should be 
         applied. 

    Returns:
        The 'flattened' object.
    """
    # Assert the type and interval of the inputs.
    AssertType(node, c4d.PolygonObject)
    AssertType(strength, (float, int))
    strength = c4d.utils.Clamp(0.0, 1.0, strength)

    # Get the document of the node. This step is only required when one wants to create an undo
    # for the operation.
    nodeDoc = node.GetDocument()
    if nodeDoc is None:
        raise RuntimeError(f"'{node.GetName()}' is not attached to a document.")

     # Get the point, polygons and polygon selection of the node.
    points = node.GetAllPoints()
    polygons = node.GetAllPolygons()
    polygonCount = len(polygons)

    # There are no polygons in #node.
    if polygonCount < 1:
        raise RuntimeError(f"'{node.GetName()}' does not contain any polygons.")

    # The current polygon selection of #node.
    baseSelect = node.GetPolygonS()

    # This is a list of boolean, e.g., for a PolygonObject with three polygons and the first and
    # third polygon being selected, it would be [True, False, True].
    polygonSelection = baseSelect.GetAll(polygonCount)

    # Get the indices of the selected polygons.
    selectedPolygonIds = [i for i, v in enumerate(polygonSelection) if v]
    selectedPolygons = [polygons[i] for i in selectedPolygonIds]

    # There are no polygons selected in #node.
    if not selectedPolygons:
        raise RuntimeError(f"'{node.GetName()}' does not contain any selected polygons.")

    # Get the points of the vertices which are part of the selected polygons.
    selectedPointIds = list({p for cpoly in selectedPolygons
                             for p in [cpoly.a, cpoly.b, cpoly.c, cpoly.d]})
    selectedPoints = [points[i] for i in selectedPointIds]

    # The selected polygon normals, the mean selected polygon normal and the mean point within the
    # polygon vertices. The mean point and the mean normal define the plane one must project points
    # into to 'flatten' the selection.
    polygonNormals = [
        GetPolygonNormal([points[cpoly.a], points[cpoly.b], points[cpoly.c]]
                         if cpoly.IsTriangle() else
                         [points[cpoly.a], points[cpoly.b], points[cpoly.c], points[cpoly.d]])
        for cpoly in selectedPolygons]
    meanNormal = ~GetMean(polygonNormals)
    meanPoint = GetMean(selectedPoints)

    # Project the selected points into the mean plane of #selectedPolygonIds and then overwrite the
    # original point, depending on #strength.
    for pid in selectedPointIds:
        p = ProjectIntoPlane(points[pid], meanPoint, meanNormal)
        # MixVec() computes the linear interpolation between two vectors.
        points[pid] = c4d.utils.MixVec(points[pid], p, strength)

    # Open an undo stack for the changes and an undo item for the point and polygon changes.
    if not nodeDoc.StartUndo():
        raise RuntimeError("Could not open undo stack.")

    if not nodeDoc.AddUndo(c4d.UNDOTYPE_CHANGE, node):
        raise RuntimeError("Could not add undo item.")

    node.SetAllPoints(points)
    node.Message(c4d.MSG_UPDATE)

    # End the undo stack.
    if not nodeDoc.EndUndo():
        raise RuntimeError("Could not close undo stack.")

    return node


def BuildSetup(doc: c4d.documents.BaseDocument) -> c4d.BaseObject:
    """Builds the inputs for the example.
    """
    def AssertType(item: any, t: typing.Type) -> any:
        if not isinstance(item, t):
            raise MemoryError(f"Could not allocate {t}.")
        return item

    # Insantiate the sphere generator.
    sphere = AssertType(c4d.BaseObject(c4d.Osphere), c4d.BaseObject)
    sphereTag = AssertType(sphere.MakeTag(c4d.Tphong), c4d.BaseTag)

    sphere[c4d.PRIM_SPHERE_TYPE] = c4d.PRIM_SPHERE_TYPE_HEXA
    sphere[c4d.PRIM_SPHERE_SUB] = 12
    sphereTag[c4d.PHONGTAG_PHONG_ANGLELIMIT] = True

    # Build the cache and insert a copy of it into #doc.
    temp = c4d.documents.BaseDocument()
    temp.InsertObject(sphere)

    if not temp.ExecutePasses(None, False, False, True, c4d.BUILDFLAGS_NONE):
        raise RuntimeError("Could not build caches for example rig.")

    cache = sphere.GetCache()
    if not isinstance(cache, c4d.PolygonObject):
        raise RuntimeError("Building caches failed.")

    clone = cache.GetClone(c4d.COPYFLAGS_NONE)
    if not isinstance(clone, c4d.PolygonObject):
        raise RuntimeError("Cloning caches failed.")

    # Set the transforms and select polygons.
    selection = clone.GetPolygonS()
    for i in (10, 11, 14, 15, 24, 25, 28, 29, 66, 67, 70, 71):
        selection.Select(i)

    # Insert the object.
    if not doc.StartUndo():
        raise RuntimeError("Could not open undo stack.")

    doc.InsertObject(clone)

    if not doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, clone):
        raise RuntimeError("Could not add undo item.")

    if not doc.EndUndo():
        raise RuntimeError("Could not close undo stack.")

    return clone


def main(doc: c4d.documents.BaseDocument, op: typing.Optional[c4d.BaseObject]) -> None:
    """Runs the example.

    Args:
        doc: The active document.
        op: The selected object in #doc. Can be #None.
    """
    # Define #node as the selected polygon object or set it to the example setup when there is no
    # polygon object selection.
    node = op if isinstance(op, c4d.PolygonObject) else BuildSetup(doc)

    # 'Flatten' the polygon selection of #node
    FlattenPolygonObjectSelection(node, 1.0)

    # Set the document to polygon mode and set the new objects as the selected object in #doc.
    doc.SetMode(c4d.Mpolygons)
    doc.SetActiveObject(node, c4d.SELECTION_NEW)

    # Inform Cinema 4D that the document has been modified.
    c4d.EventAdd()


if __name__ == '__main__':
    c4d.CallCommand(13957)  # Clear the console.
    # #doc and #op are predefined module attributes as defined at the top of the file.
    main(doc, op)
