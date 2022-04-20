#coding: utf-8
"""Demonstrates how to use the SendModellingCommand (SMC) function in general at the example of the 
'Extrude' tool.

Extrudes the active selection of the currently selected polygon object in the mode the active 
document is currently in (point, edge, or polygon mode). The active document has to be in one of
these three modes for the script to succeed.

Topics:
    * The 'Extrude' tool
    * c4d.utils.SendModellingCommand()

Overview:
    There are in principle two ways to execute modelling commands: In the original document a node
    is contained or in a dummy document. This latter case is carried out by creating a dummy 
    document just for the command, cloning the relevant nodes into that document, and then executing
    the command there. In most cases, executing a modelling command in the original document which 
    could be a loaded document, and therefore subject to threading restrictions, will cause no 
    issues, but there are some notable exceptions:
    
      * SMC calls which are not done from a non-main thread for a node in a loaded document.
      * Tools or tasks for which the complexity of a document directly impacts runtime of the tool
        but not the not the result of the tool; imagine huge amounts of irrelevant data the tool 
        might has to traverse.
      * Some tools require setups which make a dummy document desirable, e.g., the 'Join' tool.
    
    But using a dummy document has also drawbacks:
      
       * It is computationally much more demanding since all relevant data has first to be copied 
         over and then back again.
       * Inserting the SMC result back into its original document can be labor-intensive when the
         result is meant to replace the original object and cannot be inserted as new object. For 
         example all BaseLink parameters in that document which link to that node must then be found
         and updated too.
       * Determining what is relevant for a tool can be hard. In some cases it might be not enough
         to copy over a single object, and instead non-obvious dependencies which influence the 
         outcome of the tool are required too. The 'Current State to Object' tool is such example, 
         as the state of an object can depend on many things as for example fields, effectors, and 
         tags. In these cases it is best to clone the whole document; documents are nodes and can 
         therefore be cloned themselves. But it will further increase the footprint of the command.
    
    Showcased in this example is primarily the more complicated case of executing the command in a 
    temporary document. But in general it is more desirable to execute SMC in the document the node
    is already contained in.
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

def main(doc: c4d.documents.BaseDocument, op: typing.Optional[c4d.BaseObject]) -> None:
    """Runs the example.

    Args:
        doc: The active document.
        op: The selected object in #doc. Can be #None.
    """
    if not isinstance(op, c4d.PolygonObject):
        raise TypeError(f"Please select a {c4d.PolygonObject} instance.")

    # Clone the node which is the target of the operation and insert it into a temporary document.
    clone = op.GetClone(c4d.COPYFLAGS_NONE)
    if not isinstance(clone, c4d.PolygonObject):
        raise RuntimeError(f"Could not clone input object {op}.")

    temp = c4d.documents.BaseDocument()
    if not isinstance(temp, c4d.documents.BaseDocument):
        raise MemoryError("Could not create new document.")
    temp.InsertObject(clone)

    # A modelling command invokes one of the modelling tools of Cinema 4D. The function takes
    # therefore container for the settings of that tool, in this case for the Extrude tool.
    bc = c4d.BaseContainer()
    bc[c4d.MDATA_EXTRUDE_PRESERVEGROUPS] = True # Preserve element groups in extrusions.
    bc[c4d.MDATA_EXTRUDE_OFFSET] = 50.0 # The extrusion depths.
    # There are many more options for that tool as exposed in toolextrude.h

    # A modelling command takes a list of objects as one of its inputs. In this case it is just a 
    # list containing the node #clone.
    objects = [clone]

    # A modelling command has also a mode of operation. The extrude tool for example behaves 
    # differently, depending on in which editor mode the document is. E.g., being in edge mode will 
    # extrude the active edge selection. The mode passed to SMC will emulate this and allows for
    # example to extrude the polygons of an object which is in a document which is in edge mode. 
    # The example here ties the SMC mode to the mode of active document. There are also more SMC
    # modes than shown here.
    docMode = doc.GetMode()
    if docMode == c4d.Mpoints:
        mode = c4d.MODELINGCOMMANDMODE_POINTSELECTION
    elif docMode == c4d.Medges:
        mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION
    elif docMode == c4d.Mpolygons:
        mode = c4d.MODELINGCOMMANDMODE_POLYGONSELECTION
    else:
        raise RuntimeError(f"Document is not in any of the modes supported by the extrude tool.")

    # Finally, a modelling command also takes a set of flags. With them the command can for example
    # be automatically wrapped in an undo. Since this example operates on a temporary 'throw-away'
    # document, the flags are being set here to the none-flag.
    flags = c4d.MODELINGCOMMANDFLAGS_NONE

    # Execute the command. Most commands return a boolean indicating the success of the operation,
    # but some commands also return collections, containing more data. See the #MCOMMAND 
    # documentation for information on a per command basis.
    res = c4d.utils.SendModelingCommand(command=c4d.ID_MODELING_EXTRUDE_TOOL, list=objects, 
                                        mode=mode, bc=bc, doc=temp, flags=flags)
    if not res:
        raise RuntimeError(f"Modelling command failed for {op}.")

    # The same call when not going the temporary document route, and instead carrying out the 
    # command directly on the node in the active document. The the file documentation for details.

    # res = c4d.utils.SendModelingCommand(command=c4d.ID_MODELING_EXTRUDE_TOOL, list=[op], 
    #                                     mode=mode, bc=toolSettings, doc=doc, flags=flags)

    # The operation has been successful at this point and #clone has now been extruded. The node can
    # be removed from the temporary document and inserted back into the original document. This
    # example will take the easy route and just insert #clone as a new object alongside the input
    # node #op.
    clone.Remove()

    # Open an undo.
    if not doc.StartUndo():
        raise RuntimeError("Could not open undo stack.")

    # Shift #clone in its local coordinate system for bounding-box size units on the x-axis (plus 
    # 50 units for good measure) and rename the node.
    offset = c4d.Vector(clone.GetRad().x * 2 + 50, 0, 0)
    clone.SetMl(clone.GetMl() * c4d.utils.MatrixMove(offset))
    clone.SetName(f"{clone.GetName()} (SMC)")

    # Insert #clone back.
    doc.InsertObject(clone)

    # Add an undo and close the stack.
    if not doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, clone):
        raise RuntimeError("Could not add undo item.")

    if not doc.EndUndo():
        raise RuntimeError("Could not close undo stack.")

    # Inform Cinema 4D that the document has been modified.
    c4d.EventAdd()


if __name__ == '__main__':
    c4d.CallCommand(13957)  # Clear the console.
    # #doc and #op are predefined module attributes as defined at the top of the file.
    main(doc, op)
