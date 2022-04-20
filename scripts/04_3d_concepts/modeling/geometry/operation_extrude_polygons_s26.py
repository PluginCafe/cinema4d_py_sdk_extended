#coding: utf-8
"""Demonstrates how to extend polygonal geometry at the example of extruding polygons.

The example will either extrude the selected polygons of the selected PolygonObject instance, or, 
when no object selection is present, generate an example geometry which then will be extruded.

Note:
    See the modelling_smc_extrude example when interested in extruding points, edges, or polygons
    with the Extrude tool in a convenient manner. This example is not about the Extrude tool but 
    about how such tool can be implemented.

Topics:
    * Extruding polygons
    * Evaluating the normals of polygons and vertices
    * Polygon selections
    * c4d.PolygonObject
    * c4d.CPolygon

Examples:
    * GetPolygonNormal(): Returns the normal of the polygon defined by the passed points.
    * ExtrudePolygonObject(): Extrudes the selected polygons in a polygon object.

Overview:
    It is not recommended to reinvent the wheel for basic operations as extruding polygons. While 
    writing their basic functionality can be trivial, implementing all functions and updating the 
    adjacent data as uv or normal data is often non-trivial or at least very labor-intensive. 
    SendModellingCommand() should be used whenever possible, as it will do all these things for 
    free. This file serves as a simple example for how such tool works which constructs geometry on
    existing geometry.
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
    """Assert the type of #item.
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


def ExtrudePolygonObject(node: c4d.PolygonObject, distance: float) -> c4d.PolygonObject:
    """Extrudes the selected polygons in a polygon object.

    Usually something like this does not have to be done, and it is better to use the existing
    modelling commands of Cinema 4D. While it is manageable to write something like an extrude
    operation, it is quite labor-intensive to do all the adjacent operations which have to be
    carried out, as for example updating UVW, custom normal, or other data. This example only 
    modifies the geometry of #node to showcase how something like this is done in principle, but
    does not update any 'adjacent' data as for example UVW data. It is also the most simplistic
    implementation possible, and does not provide features as extruding 'islands' and negative 
    extrusion depths.

    Args:
        node: The polygon object to extrude the selected polygon.
        distance: The distance of extrusion. Must be a positive value. When wanting to support
         negative values, one would have to invert the polygon normals when #distance is negative.
    """
    # Assert the type of the inputs.
    AssertType(node, c4d.PolygonObject)
    AssertType(distance, (float, int))
    distance = max(distance, 0.0)

    # Get the document of the node. This step is only required when one wants to create an undo
    # for the operation.
    nodeDoc = node.GetDocument()
    if nodeDoc is None:
        raise RuntimeError(f"'{node.GetName()}' is not attached to a document.")

    # Get the polygon selection of #node and find the selected indices in it.
    selection = node.GetPolygonS()

    # This is a list of boolean, e.g., for a PolygonObject with three polygons and the first and
    # third polygon being selected, it would be [True, False, True].
    states = selection.GetAll(node.GetPolygonCount())

    # Translate #states into a list of selected indices.
    selectedPolygonIndices = tuple(i for i, n in enumerate(states) if n)

    if len(selectedPolygonIndices) == 0:
        raise RuntimeError(f"'{node.GetName()}' does not contain any selected polygons.")

    # Get the polygons and points of #node.
    points = node.GetAllPoints()
    polygons = node.GetAllPolygons()

    # The maximum polygon index before modifications minus the count of polygons which will be
    # extruded and therefore removed. Storing this value is required to create the optional new
    # polygon selection state after the operation has been carried out.
    oldAdjustedMaxPolygonIndex = (len(polygons)) - len(selectedPolygonIndices)

    # Loop over all polygons indices which should be extruded.
    for pid in selectedPolygonIndices:

        # A polygon which should be extruded.
        cpoly = polygons[pid]

        # Get the vertex indices of the polygon and the points for these vertices. Since Cinema 4D
        # does store even triangles with a fourth index, one can blindly index a polygon as a quad
        # and only differentiate the two cases when it matters.
        ia, ib, ic, id = cpoly.a, cpoly.b, cpoly.c, cpoly.d
        a, b, c, d = points[ia], points[ib], points[ic], points[id]
        isTriangle = cpoly.IsTriangle()

        # Get the normal of the selected polygon.
        normal = GetPolygonNormal((a, b, c) if isTriangle else (a, b, c, d))

        # A diagram of the operation of extruding the polygon #P.
        #
        #         d'------- c'
        #        /|        /|
        #       / |       / |
        #      a'------- b' |/
        #     -|- d -----|- c --
        #      | /   P   | /
        #      |/        |/
        #   -- a ------- b --
        #     /         /
        #
        #   P                 The to be extruded (and removed) polygon.
        #   a, b, c, d        The vertices of the to be extruded polygon #P.
        #   a', b', c', d'    The extruded vertices.

        # Extrude the points. An extruded point is defined as the sum of the original point and the
        # the polygon normal scaled to the extrusion depth.
        a_ = a + normal * distance
        b_ = b + normal * distance
        c_ = c + normal * distance
        d_ = d + normal * distance  # Only relevant when #isTriangle is #False.

        # Determine the indices of the new points.
        start = len(points) - 1
        ia_, ib_, ic_, id_ = start + 1, start + 2, start + 3, start + 4
        # Append the new points to the existing points of the object. When the to be extruded
        # polygon is a triangle, the fourth point #d must be excluded.
        points += [a_, b_, c_] if isTriangle else [a_, b_, c_, d_]

        # Construct the new polygons. Just as for constructing the cube object example, the order
        # of polygons does not carry and special meaning, but the order of vertices does, as it will
        # determine the normal of the polygon. See the example function ConstructPolygonObject() in
        # geometry_types_xxx.py which constructs a cube object for fundamental information on
        # polygons and polygon objects.
        #
        #         d'------- c'
        #        /|        /|
        #       / |       / |
        #      a'------- b' |/
        #     -|- d -----|- c --
        #      | /   P   | /
        #      |/        |/
        #   -- a ------- b --
        #     /         /
        #
        newPolygons = [
            # The to be extruded polygon is a quadrangle.
            c4d.CPolygon(ia_, ib_, ic_, id_),  # The polygon at the top
            c4d.CPolygon(ia, ib, ib_, ia_),   # The polygon for the edge #ab
            c4d.CPolygon(ib, ic, ic_, ib_),   # The polygon for the edge #bc
            c4d.CPolygon(ic_, ic, id, id_),   # The polygon for the edge #cd
            c4d.CPolygon(id_, id, ia, ia_),   # The polygon for the edge #da
        ] if not isTriangle else [
            # The to be extruded polygon is a triangle.
            c4d.CPolygon(ia_, ib_, ic_, ic_),  # The polygon at the top
            c4d.CPolygon(ia, ib, ib_, ia_),   # The polygon for the edge #ab
            c4d.CPolygon(ib, ic, ic_, ib_),   # The polygon for the edge #bc
            c4d.CPolygon(ic_, ic, ia, ia_)    # The polygon for the edge #ca
        ]

        # Append the new polygons to the list of polygons of the object.
        polygons += newPolygons

    # End of loop

    # Remove all polygons which have been extruded from the list of polygons. The principal state
    # of #polygons is as follows, where indices marked as {} are polygons which have been extruded,
    # and should be removed, and indices marked with () are new polygons which have been added.
    # i + n marks the old maximum polygon index before the extrusions and i + n + m the new maximum
    # index.
    #
    #   polygons = [i, {i + 1}, i + 2, ..., i + n, (i + n + 1), (i + n + 2), ..., (i + n + m)]
    #
    polygons = [cpoly for i, cpoly in enumerate(polygons) if i not in selectedPolygonIndices]

    # Start an undo operation.
    doc.StartUndo()
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, node)

    # The polygon object must be resized before the data can be written back.
    node.ResizeObject(pcnt=len(points), vcnt=len(polygons))

    # Open an undo stack for the changes and an undo item for the point and polygon changes.
    if not nodeDoc.StartUndo():
        raise RuntimeError("Could not open undo stack.")

    if not nodeDoc.AddUndo(c4d.UNDOTYPE_CHANGE, node):
        raise RuntimeError("Could not add undo item.")

    # Write the data back to the polygon object.
    node.SetAllPoints(points)
    for i, cpoly in enumerate(polygons):
        node.SetPolygon(i, cpoly)

    node.Message(c4d.MSG_UPDATE)

    # It is technically not necessary to do this, but since the polygon count has changed, the
    # polygon selection state of #node is now incorrect, as selections reference indices. Being
    # selected are here all new polygons.
    if not nodeDoc.AddUndo(c4d.UNDOTYPE_CHANGE_SELECTION, node):
        raise RuntimeError("Could not add undo item.")

    # Flush the polygon selection.
    selection.DeselectAll()

    # Select all new polygons which have been appended to the list of polygons.
    for i in range(oldAdjustedMaxPolygonIndex, node.GetPolygonCount()):
        selection.Select(i)

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

    # Instantiate the sphere generator.
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

    # Extrude the selected polygons in #node manually by 50 units.
    ExtrudePolygonObject(node, 50.)

    # Set the document to polygon mode and set #node as the selected object in #doc.
    doc.SetMode(c4d.Mpolygons)
    doc.SetActiveObject(node, c4d.SELECTION_NEW)

    # Inform Cinema 4D that the document has been modified.
    c4d.EventAdd()


if __name__ == '__main__':
    c4d.CallCommand(13957)  # Clear the console.
    # #doc and #op are predefined module attributes as defined at the top of the file.
    main(doc, op)
