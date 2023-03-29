#coding: utf-8
"""Demonstrates how to 'transfer' the axis of a point object to another object while keeping its 
vertices in place.

The example requires at least two objects in the scene of which one must be selected and a 
PointObject instance. The script will open a popup, letting the user select a target object. The 
axis of the selected object will then be 'transferred' to the axis of the target while keeping its 
vertices in place.

Topics:
    * Transferring the axis of an object
    * The inverse of a transform
    * c4d.PointObject
    * c4d.Matrix

Examples:
    * TransferAxisTo(): Transforms the coordinate system of #node to #target while keeping its 
     vertices in place.

Overview:
    The axis of a PointObject does not exist as the separately manipulatable entity in the API as it
    does in the application. Objects only have a coordinate system which is displayed as their axis
    in the application. Transforming that coordinate system will also transform everything which
    is governed by it, as vertices and child objects of the object. To transform the axis of an 
    object without transforming its points, one first must transform the object to the desired state
    and then apply the inverse of that transform to all points of the object. Which will result in 
    the points occupying the same world coordinates after the operation, but the object having a new
    coordinate system, i.e., what is displayed as its axis.
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


def TransferAxisTo(node: c4d.PointObject, target: c4d.BaseObject) -> None:
    """Transforms the coordinate system of #node to #target while keeping its vertices in place.

    Args:
        node: The object to transfer the axis for.
        target: The object to transfer the axis to.
    """
    if not isinstance(node, c4d.PointObject):
        raise TypeError(f"Expected {c4d.PointObject} for {node}.")

    # Get the global matrix of #node and #target which are the absolute transforms, i.e., absolute
    # coordinate systems which govern these two objects.
    mgNode = node.GetMg()
    mgTarget = target.GetMg()

    # Get the document of #node.
    nodeDoc = node.GetDocument()
    if nodeDoc is None:
        raise RuntimeError(f"'{node.GetName()}' is not attached to a document.")

    # Open an undo stack for the changes and add an undo item for the point and matrix changes.
    if not nodeDoc.StartUndo():
        raise RuntimeError("Could not open undo stack.")

    if not nodeDoc.AddUndo(c4d.UNDOTYPE_CHANGE, node):
        raise RuntimeError("Could not add undo item.")

    # Set the transform of #node to the target transform. The axis of #node is now at the desired 
    # location, but its points have also been implicitly transformed as they are expressed in 
    # relation to the coordinate system of #node.
    node.SetMg(mgTarget)

    # The ~ operator returns the inverse of a matrix/transform. When a transform translates by +50 
    # units on the x-axis and then rotates by +π units on the y-axis, the inverse of that transform 
    # will translate by -50 units on the x-axis and then rotate by -π units on the y-axis. Because 
    # of that, for a transform #T and a point #p, the following equation holds true.
    #
    #   p * T * ~T = p
    #
    # Compute the difference between the old transform of #node and its new state at #target by
    # multiplying the inverse of #mgNode with #mgTarget. #mgDelta will therefore be the transform
    # which is required to transform from #mgNode to #mgTarget. 
    mgDelta = ~mgNode * mgTarget

    # Multiply all points of #node by the inverse of that delta to "undo" the transform which has
    # been implicitly applied to them, when the coordinate system of #node they live in, has been 
    # changed by setting its global matrix to #mgTarget.
    node.SetAllPoints([p * ~mgDelta for p in node.GetAllPoints()])
    node.Message(c4d.MSG_UPDATE)

    # If node has any child objects, this "undoing" of the transform must also be applied to them. 
    # This step has been left out here to keep the core of this example simple.

    if not nodeDoc.EndUndo():
        raise RuntimeError("Could not close undo stack.")


def GetAllNodes(node: c4d.GeListNode) -> c4d.GeListNode:
    """Yields all descendants of #node, including #node itself.

    Args:
        node: The node to yield descendants for.

    Yields:
        A descendant of #node.
    """
    if node is None:
        return

    while node:
        yield node

        for descendant in GetAllNodes(node.GetDown()):
            yield descendant

        node = node.GetNext()


def main(doc: c4d.documents.BaseDocument, op: typing.Optional[c4d.BaseObject]):
    """Runs the example.

    Args:
        doc: The active document.
        op: The selected object in #doc. Can be #None.
    """
    if not isinstance(op, c4d.BaseObject):
        raise RuntimeError("Please select an object.")

    # Get all objects in the scene as a list and remove #op from it.
    objects = list(GetAllNodes(doc.GetFirstObject()))
    objects.remove(op)
    if len(objects) < 1:
        raise RuntimeError("There are no other objects to transfer the axis to.")

    # Build and show a popup menu for all objects with their name and icon.
    bc, idBase = c4d.BaseContainer(), 1000
    for i, node in enumerate(objects):
        bc.InsData(idBase + i, f"{node.GetName()}&i{node.GetType()}&")
    res = c4d.gui.ShowPopupDialog(None, bc, c4d.MOUSEPOS, c4d.MOUSEPOS)

    # The user did abort the popup.
    if res == 0:
        return

    # Carry out the operation.
    target = objects[res - idBase]
    TransferAxisTo(op, target)

    # Inform Cinema 4D that the document has been modified.
    c4d.EventAdd()


if __name__ == '__main__':
    c4d.CallCommand(13957)  # Clear the console.
    # #doc and #op are predefined module attributes as defined at the top of the file.
    main(doc, op)
