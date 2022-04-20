#coding: utf-8
"""Explains the user-editable polygon object model of the classic API.

The example constructs a simple polygonal cube object.

Topics:
    * Constructing polygon objects
    * c4d.PointObject
    * c4d.PolygonObject
    * c4d.CPolygon

Examples:
    * ConstructPolygonObject(): Demonstrates constructing polygon objects at the example of a cube.

Overview:
    User-editable polygon object are represented by the type PolygonObject which is derived form 
    PointObject. PolygonObject instances haves points expressed as Vector instances and polygons 
    expressed asCPolygon instances. But there is no type which represent edges, as edges are only a
    virtual concept that is only indirectly accessible through selections.

    The vertex and polygon normals which are formed by a PolygonObject are not exposed directly. 
    Instead, only sets of (possibly) interpolated vertex normals can be accessible by either a 
    PhongTag or NormalTag attached to the polygon object; but there is no guarantee that they are
    present. Which in turn means that the non-interpolated vertex or polygon normals should be 
    computed manually in Python.
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


def ConstructPolygonObject(doc: c4d.documents.BaseDocument) -> None:
    """Demonstrates constructing polygon objects at the example of a cube.

    Args:
        doc: The active document.
    """
    print ("\n\n--- ConstructPolygonObject Example -----------------------------------------------")

    # Polygon objects are represented by the type PolygonObject. The two arguments to the 
    # initializer of the type describe the point (first) and polygon (second) count the object will
    # be able to hold.
    cube = c4d.PolygonObject(pcnt=8, vcnt=6)
    if not isinstance(cube, c4d.PolygonObject):
        raise MemoryError("Could not allocate polygon object.")

    # PolygonObject is derived from PointObject and provides therefore access to a set of points for
    # the vertices of the object. The points are expressed as c4d.Vector instances in the local 
    # space of the object.
    points = cube.GetAllPoints()

    # The transform of the object, i.e., what is shown as the axis of the object in the viewport.
    # All vectors in #points are expressed in relation to this coordinate system.
    mg = cube.GetMg()

    # A polygon object also provides access to a set of polygons.
    polygons = cube.GetAllPolygons()

    # But there is no such thing as GetAllEdges(), as edges are only an abstract concept that is
    # not reflected in types or explicitly stored data.

    print (f"\nPoints and polygons of '{cube.GetName()}' after allocation:")
    print(f"{cube.GetAllPoints() = }")
    print(f"{cube.GetAllPolygons() = }")

    # One method to generate new geometry is to manually construct it. It is not necessary to 
    # retrieve the existing point and polygon lists of a polygon object for that, unless it is the 
    # explicit goal to extend existing polygonal geometry.

    # The following code will construct a simple cube geometry with this layout:
    #
    #       3 ------- 2
    #      /|        /|
    #     / |       / |
    #    0 ------- 1  |
    #    |  7 -----|- 6
    #    | /       | /
    #    |/        |/
    #    4 ------- 5
    #
    # Where the point #4 is also the origin of the object.

    # The side length of the cube.
    size = 100.0

    # The points of the cube.
    points = [
        c4d.Vector(0, size, 0),            # Point 0
        c4d.Vector(size, size, 0),         # Point 1
        c4d.Vector(size, size, size),      # Point 2
        c4d.Vector(0, size, size),         # Point 3
        c4d.Vector(0, 0, 0),               # Point 4
        c4d.Vector(size, 0, 0),            # Point 5
        c4d.Vector(size, 0, size),         # Point 6
        c4d.Vector(0, 0, size),            # Point 7
    ]

    # Polygons are represented by the type CPolygon. A CPolygon instance does index four points in
    # the PolygonObject (which is also a PointObject) it is attached to.

    # A CPolygon instance, its index values become only meaningful in conjunction with a set of
    # points provided by a PolygonObject.
    quad = c4d.CPolygon(0, 1, 2, 3)

    # The type provides access to the four fields #a, #b, #c, and #d, but they store only the 
    # indices passed to the initializer of the instance and not the points they reference.
    print (f"\n{quad.a = }, {quad.b = }, {quad.c = }, {quad.d = }")

    # The order of point indices matters, inverting the point order will also invert the normal of 
    # the polygon.
    inverted = c4d.CPolygon(3, 2, 1, 0)

    # Not only quadrangles are stored in this fashion, but also triangles. A triangle will simply 
    # repeat its last index.
    tri = c4d.CPolygon(0, 1, 2, 2)

    # This can also be tested with the method IsTriangle() instead of comparing #c and #d.
    print (f"\n{quad.IsTriangle() = }")
    print (f"{tri.IsTriangle() = }")

    # Constructing the polygons for the cube:
    #
    #
    #       3 ------- 2
    #      /|        /|
    #     / |       / |
    #    0 ------- 1  |
    #    |  7 -----|- 6
    #    | /       | /
    #    |/        |/
    #    4 ------- 5
    #

    polygons = [
        # Constructing the first polygon which makes up the top of the cube. 
        #
        #       3 ------- 2
        #      /|        /|
        #     / |       / |
        #    0 ------- 1  |
        #    |         |
        #
        # The order (3, 2, 1, 0) in which the points are being placed might seem counter-intuitive. 
        # This order is caused by the fact that the point order determines the normal of the 
        # polygon. The tuples (2, 1, 0, 3), (1, 0, 3, 2), and (0, 3, 2, 1) would all be valid 
        # alternatives to represent this polygon, but the tuple (0, 1, 2, 3) would for example be 
        # not. 
        # 
        # The normal of a polygon is determined by the cross product of the edges of its vertices.
        # When applying the right-hand-rule to the vectors #a = (0, 1) and #b = (2, 1), the two 
        # edge vectors for the edges adjacent to the point #1, one's thumb must point downwards 
        # when aligning the index finger with the vector #a and the middle finger with the vector 
        # #b. However, when switching the order of the two edges, and #a is (2, 1) and #b is (0, 1), 
        # one's thumb will point upwards, the direction the normal of that polygon should point to. 
        # The vertices must therefore be placed in a clockwise order (in relation to the diagram) 
        # to have the polygon normal face into the desired direction. If seems overly complicated,
        # trial and error is also a valid option ;)
        c4d.CPolygon(3, 2, 1, 0),

        # The bottom side. There is no need for putting the polygons in any 'logical' order, a 
        # polygon array can jump all over the place in its geometry, but the order in which the 
        # polygons are placed in the list will determine the polygon index of each polygon, so it 
        # might be desirable to place them in a logical order for the convenience of the user.
        #
        #       |         |
        #    |  7 -----|- 6
        #    | /       | /
        #    |/        |/
        #    4 ------- 5
        c4d.CPolygon(4, 5, 6, 7),

        # The left side.
        #
        #       3 ---
        #      /|
        #     / |
        #    0 --- 
        #    |  7 ---
        #    | /     
        #    |/ 
        #    4 ---
        c4d.CPolygon(0, 4, 7, 3),

        # The right side.
        #
        #             --- 2
        #                /|
        #               / |
        #          --- 1  |
        #             -|- 6
        #              | /
        #              |/
        #          --- 5
        c4d.CPolygon(1, 2, 6, 5),

        # The front side.
        #
        #     /         / 
        #    0 ------- 1  
        #    |         |
        #    |         | 
        #    |         |/
        #    4 ------- 5
        c4d.CPolygon(0, 1, 5, 4),

        # The back side.
        #
        #       3 ------- 2
        #      /|        /|
        #       |         |
        #       |         |
        #       7 ------- 6
        #      /         /
        c4d.CPolygon(3, 7, 6, 2),
    ]

    # The points of a point object can be set at once with the method PointObject.SetAllPoints().
    cube.SetAllPoints(points)

    # But polygons must be set one by one with PolygonObject.SetPolygon() in the Python API.
    for i, cpoly in enumerate(polygons):
        cube.SetPolygon(i, cpoly)

    # After updating the vertices of a PointObject, the message MSG_UPDATE should be sent to it.
    cube.Message(c4d.MSG_UPDATE)

    print (f"\nPoints and polygons of '{cube.GetName()}' after modification:")
    print(f"{cube.GetAllPoints() = }")
    print(f"{cube.GetAllPolygons() = }")

    return cube

def main(doc: c4d.documents.BaseDocument) -> None:
    """Runs the example.

    Args:
        doc: The active document.
    """
    # Run the example constructing a polygon object.
    cube = ConstructPolygonObject(doc)

     # Insert the polygon object into the document, wrapping the operation into an undo.
    if not doc.StartUndo():
        raise RuntimeError("Could not open undo stack.")

    doc.InsertObject(cube)

    if not doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, cube):
        raise RuntimeError("Could not add undo item.")

    if not doc.EndUndo():
        raise RuntimeError("Could not close undo stack.")

    # Set the document to polygon mode and select the new object.
    doc.SetMode(c4d.Mpolygons)
    doc.SetActiveObject(cube, c4d.SELECTION_NEW)

    # Inform Cinema 4D that the document has been modified.
    c4d.EventAdd()


if __name__ == '__main__':
    c4d.CallCommand(13957) # Clear the console.
    # doc is a predefined module attribute as defined at the top of the file.
    main(doc)
