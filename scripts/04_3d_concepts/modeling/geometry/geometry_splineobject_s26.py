#coding: utf-8
"""Explains the user-editable spline object model of the classic API.

The example constructs two spline objects, one without tangents and one with tangents.

Topics:
    * Constructing spline objects
    * c4d.PointObject
    * c4d.SplineObject

Examples:
    * ConstructSplineObject(): Demonstrates constructing linear and Bezier spline objects.

Overview:
    User-editable spline object are represented by the type SplineObject which is derived from 
    PointObject. Other than PolygonObject, a SplineObject instance is a generator object and has an 
    underlying cache, a LineObject instance. A LineObject represents a SplineObject and its 
    interpolation settings as a series of line segments.

    SplineObject instances can be composed out of disjunct segments, which are not be confused with
    the segments of a LineObject. Imagine for example two circles that are part of the same spline, 
    where each circle is then a segment in that spline. But other than polygons, segments do not 
    have their own dedicated type and are handled with the type SplineObject directly.

    Splines also have an interpolation type and interpolation settings. The five interpolation types
    of splines in Cinema 4D are:

        Linear:    A spline with no vertex tangents that will interpolate linearly between two 
                    vertices.
        Cubic:     A spline with no vertex tangents that will interpolate with cubic-hermite 
                    interpolation between two vertices.
        Akima:     A spline with no vertex tangents that will interpolate with Akima interpolation
                    between two vertices.
        B-Spline:  A spline with no vertex tangents that will interpolate with B-Spline
                    interpolation between two vertices.
        Bezier:    A spline with user-definable vertex tangents that will interpolate with Bezier 
                    interpolation between two vertices.
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


def ConstructSplineObject() -> tuple[c4d.SplineObject]:
    """Demonstrates constructing linear and Bezier spline objects.

    Args:
        doc: The active document.
    
    Returns:
        The two constructed spline objects.
    """
    # --- Linear Spline ----------------------------------------------------------------------------

    # Create a spline with eight points which is of linear interpolation type.
    linSpline = c4d.SplineObject(pcnt=8, type=c4d.SPLINETYPE_LINEAR)
    if not isinstance(linSpline, c4d.SplineObject):
        raise MemoryError("Could not allocate spline object.")

    # SplineObject is derived from PointObject and provides therefore access to a set of points for
    # the vertices of the object. The points are expressed as c4d.Vector instances in the local
    # space of the object.
    points = linSpline.GetAllPoints()

    # The transform of the object, i.e., what is shown as the axis of the object in the viewport.
    # All vectors in #points are expressed in relation to this coordinate system.
    mg = linSpline.GetMg()

    # The points of a spline will all be the null-vector after allocation.
    print("\nPoints of 'Linear Spline' after allocation:")
    print(f"{linSpline.GetAllPoints() = }")

    # Splines can be closed or not closed. A closed spline will loop from its last vertex to its
    # first vertex.
    isClosed = linSpline.IsClosed()

    # This closed state can be set in the context of segments locally, as shown later, or globally
    # for a spline with the "Closed" parameter of the spline object.
    linSpline[c4d.SPLINEOBJECT_CLOSED] = True

    # The following code will construct a spline containing two closed diamond shapes. Each diamond
    # is defined over four vertices and there are two segments in the spline (one for each diamond).
    #
    #      1               5
    #     / \             / \
    #    0   2  <- d ->  4   6
    #     . /             . /
    #      3               7
    #
    # The origin of the spline will lie on the point #0. The distance #d between the diamonds will
    # be equal to the width of a diamond, i.e., |p0 - p2| == |p2 - p4|.

    # The width and height of a diamond shape.
    size = 200.0
    # Half the size.
    halfSize = size * .5
    # The x-axis offset for the second diamond segment.
    offset = c4d.Vector(2 * size, 0, 0)

    # The points for the spline.
    points = [
        # First diamond
        c4d.Vector(0, 0, 0),                          # Point 0
        c4d.Vector(halfSize, halfSize, 0),            # Point 1
        c4d.Vector(size, 0, 0),                       # Point 2
        c4d.Vector(halfSize, -halfSize, 0),           # Point 3
        # Second Diamond
        c4d.Vector(0, 0, 0) + offset,                 # Point 4
        c4d.Vector(halfSize, halfSize, 0) + offset,   # Point 5
        c4d.Vector(size, 0, 0) + offset,              # Point 6
        c4d.Vector(halfSize, -halfSize, 0) + offset   # Point 7
    ]

    # Since the data requires two segments, the spline object must be resized before adding the
    # points. The first argument is the point count and the second argument is the number of
    # segments in the spline.
    if not linSpline.ResizeObject(pcnt=8, scnt=2):
        raise RuntimeError("Could not resize spline object.")

    # The points of a point object must be set with the method PointObject.SetAllPoints().
    linSpline.SetAllPoints(points)

    # At this point, the spline would still be one continuous segment.
    #
    #      1      5
    #     / \    / \
    #    0   2  4   6
    #       /  /    /
    #      3 _/    7
    #

    # To change that, the two segments of the spline must be defined. The argument #cnt to the
    # method SplineObject.SetSegment() defines the point indices of a segment in relation to the
    # previous segment. Setting the point count for the first segment to four points will included
    # the points #0 to #3, and setting the second segment to four points, will included the
    # following four points, the points #4 to #7.
    linSpline.SetSegment(id=0, cnt=4, closed=True)
    linSpline.SetSegment(id=1, cnt=4, closed=True)

    # After updating the vertices of a PointObject, the message MSG_UPDATE should be sent to it.
    linSpline.Message(c4d.MSG_UPDATE)

    print("\nPoints of 'Linear Spline' after modification:")
    print(f"{linSpline.GetAllPoints() = }")

    # Set the name and position of the spline.
    linSpline.SetName("Linear Spline")
    linSpline.SetMg(c4d.utils.MatrixMove(c4d.Vector(-300, 0, 150)))

    # --- Bezier Spline ----------------------------------------------------------------------------

    # Create a spline with eight points which has the Bezier interpolation type.
    bezSpline = c4d.SplineObject(pcnt=8, type=c4d.SPLINETYPE_BEZIER)
    if not isinstance(bezSpline, c4d.SplineObject):
        raise MemoryError("Could not allocate spline object.")

    # Close the spline.
    bezSpline[c4d.SPLINEOBJECT_CLOSED] = True

    # The following code will construct a spline containing two closed diamond shapes just as the
    # linear spline example (the point data will be reused in fact).
    #
    #      1               5
    #     / \             / \
    #    0   2           4   6
    #     . /             . /
    #      3               7
    #
    # But since this is a Bezier spline with user controlled vertex tangents, the code will also
    # set the tangents of the spline. The tangent layout for a singular diamond will be as follows.
    #
    #           x--b--x
    #          x /   \ x
    #          |/     \|
    #          a       c
    #          |\     /|
    #          x \   / x
    #           x--d--x
    #
    # Which will cause the two diamond shapes to approximately take the shape of a circle.

    # Resize the spline object to add a second segment.
    if not bezSpline.ResizeObject(pcnt=8, scnt=2):
        raise RuntimeError("Could not resize spline object.")

    # Set the points, reusing the points from the linear spline case.
    bezSpline.SetAllPoints(points)

    # Set the segments, just as in the linear case.
    bezSpline.SetSegment(id=0, cnt=4, closed=True)
    bezSpline.SetSegment(id=1, cnt=4, closed=True)

    # Define the tangents for the spline.

    # Each vertex #p has two tangents #t1 and #t2, where #t1 is the tangent that is adjacent to the
    # the predecessor vertex #o of #p, and #t2 is the tangent that is adjacent to the successor
    # vertex #q of #p
    #
    #                    t1 ---- p ---- t2
    #                           / \
    #                          o   q
    #

    # The length of a tangent as 20% of the height/width of the diamond shape. There is no higher
    # insight behind this value, it just happens to produce an output that is visually similar to
    # a circle.
    tLength = size * .2

    # Since tangents are defined in relation to a vertex and the tangents in this spline are very
    # symmetrical, it is here sufficient to just define two vectors for the tangents and reuse them.
    th = c4d.Vector(tLength, 0, 0)  # A horizontal tangent.
    tv = c4d.Vector(0, tLength, 0)  # A vertical tangent.

    #
    #      1               5
    #     / \             / \
    #    0   2           4   6
    #     . /             . /
    #      3               7
    #

    # The tangents for the spline as a list of tangent pairs for each vertex.
    tangents = [
        (-tv, tv),  # For vertex #0
        (-th, th),  # For vertex #1
        (tv, -tv),  # For vertex #2
        (th, -th),  # For vertex #3
        (-tv, tv),  # For vertex #4
        (-th, th),  # For vertex #5
        (tv, -tv),  # For vertex #6
        (th, -th),  # For vertex #7
    ]

    # Tangents must be set with the method SetTangent(), taking the vertex index #id, the
    # tangent adjacent to the predecessor #vl, and the tangent adjacent to the successor #vr
    # for a vertex.
    for i, pair in enumerate(tangents):
        bezSpline.SetTangent(id=i, vl=pair[0], vr=pair[1])

    # After updating the points of a PointObject, the message MSG_UPDATE must be sent to it.
    bezSpline.Message(c4d.MSG_UPDATE)

    # Set the name and position of the spline.
    bezSpline.SetName("Bezier Spline")
    bezSpline.SetMg(c4d.utils.MatrixMove(c4d.Vector(-300, 0, -150)))
    
    return (linSpline, bezSpline)


def main(doc: c4d.documents.BaseDocument) -> None:
    """Runs the example.

    Args:
        doc: The active document.
    """
    # Run the example constructing the two spline objects.
    linSpline, bezSpline = ConstructSplineObject()

    # Insert both spline objects into the document wrapped into an undo.
    if not doc.StartUndo():
        raise RuntimeError("Could not open undo stack.")

    doc.InsertObject(linSpline)

    if not doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, linSpline):
        raise RuntimeError("Could not add undo item.")

    doc.InsertObject(bezSpline)

    if not doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, bezSpline):
        raise RuntimeError("Could not add undo item.")

    if not doc.EndUndo():
        raise RuntimeError("Could not close undo stack.")

    # Set the document to point mode and select both splines.
    doc.SetMode(c4d.Mpoints)
    doc.SetActiveObject(linSpline, c4d.SELECTION_NEW)
    doc.SetActiveObject(bezSpline, c4d.SELECTION_ADD)

    # Inform Cinema 4D that the document has been modified.
    c4d.EventAdd()


if __name__ == '__main__':
    c4d.CallCommand(13957)  # Clear the console.
    # doc is a predefined module attribute as defined at the top of the file.
    main(doc)
