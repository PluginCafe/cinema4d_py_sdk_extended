#coding: utf-8
"""Demonstrates how to use the `SendModelingCommand` (SMC) function in general at the example of the 
'Extrude' tool.

Extrudes the active selection of the currently selected polygon object in the mode the active 
document is currently in (point, edge, or polygon mode). The active document has to be in one of
these three modes for the script to succeed.

Topics:
    * The 'Extrude' tool
    * c4d.utils.SendModelingCommand()

Overview:
    There are in principle two ways to execute modeling commands: In the original document a node
    is contained in or in a dummy document. The latter case is carried out by creating a dummy 
    document just for the command, cloning the relevant node(s) into that document, and then 
    executing the command there. In most cases, executing a modeling command in the original 
    document - which could be a loaded document and therefore subject to threading restrictions - 
    will cause no issues, but there are some notable exceptions:
    
      * SMC calls which are not done from a non-main thread context for a node in a loaded document.
        This could for example be an SMC call in an object plugins GetVirtualObjects method that is
        meant to modify an input object of the plugin. Think of an extrude object plugin that has 
        for example the option to bevel its input spline.
      * Tools or tasks for which the complexity of a document directly impacts runtime of the tool
        but not the result of the tool; imagine a huge amount of irrelevant data the tool might has 
        to traverse.
      * Some tools require setups which make a dummy document desirable, e.g., the 'Join' tool.
    
    But using a dummy document has also drawbacks:
      
       * It is computationally much more demanding since all relevant data has first to be copied 
         over to the dummy document and often then also back again to an 'original' document.
       * Inserting the SMC result back into its original document can be labour-intensive when the
         result is meant to replace the original object and cannot be inserted as a new object. For 
         example all BaseLink parameters in that document which link to that node must then be found
         and updated too.
       * Determining what is relevant for a tool can be hard. In some cases it might not be enough
         to copy over a single object, and instead non-obvious dependencies which influence the 
         outcome of the tool are required too. The 'Current State to Object' tool is such example, 
         as the state of an object can depend on many things as for example fields, effectors, and 
         tags. In these cases it is best to clone the whole document; documents are nodes and can 
         therefore be cloned themselves. But it will further increase the time and memory complexity
         problem of the approach.
    
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

    # A modeling command invokes one of the modeling tools of Cinema 4D. The function takes
    # therefore container for the settings of that tool, in this case for the Extrude tool.
    bc = c4d.BaseContainer()
    bc[c4d.MDATA_EXTRUDE_PRESERVEGROUPS] = True # Preserve element groups in extrusions.
    bc[c4d.MDATA_EXTRUDE_OFFSET] = 50.0 # The extrusion depths.
    # There are many more options for that tool as exposed in toolextrude.h

    # A modeling command takes a list of objects as one of its inputs. In this case it is just a 
    # list containing the node #clone.
    objects = [clone]

    # A modeling command has also a mode of operation. The extrude tool for example behaves 
    # differently, depending on in which editor mode (point, edge, polygon, object) the document 
    # is in. E.g., being in edge mode will extrude the active edge selection. The example here ties 
    # the SMC mode to the mode of active document. There are also more SMC modes than shown here.
    docMode = doc.GetMode()
    if docMode == c4d.Mpoints:
        mode = c4d.MODELINGCOMMANDMODE_POINTSELECTION
    elif docMode == c4d.Medges:
        mode = c4d.MODELINGCOMMANDMODE_EDGESELECTION
    elif docMode == c4d.Mpolygons:
        mode = c4d.MODELINGCOMMANDMODE_POLYGONSELECTION
    else:
        raise RuntimeError(f"Document is not in any of the modes supported by the extrude tool.")

    # Finally, a modeling command also takes a set of flags. With them the command can for example
    # be automatically wrapped in an undo. Since this example operates on a temporary 'throw-away'
    # document, the flags are being set here to the none-flag.
    flags = c4d.MODELINGCOMMANDFLAGS_NONE

    # Execute the command. Most commands return a boolean indicating the success of the operation,
    # but some commands also return collections, containing more data. See the #MCOMMAND 
    # documentation for information on a per command basis.
    res = c4d.utils.SendModelingCommand(command=c4d.ID_MODELING_EXTRUDE_TOOL, list=objects, 
                                        mode=mode, bc=bc, doc=temp, flags=flags)
    if not res:
        raise RuntimeError(f"modeling command failed for {op}.")

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

    # Rename the node and insert it back.
    clone.SetName(f"{clone.GetName()} (SMC)")
    doc.InsertObject(clone)

    # Add an undo and close the stack.
    if not doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, clone):
        raise RuntimeError("Could not add undo item.")

    if not doc.EndUndo():
        raise RuntimeError("Could not close undo stack.")

    # Inform Cinema 4D that the document has been modified.
    c4d.EventAdd()


if __name__ == '__main__':
    # #doc and #op are predefined module attributes as defined at the top of the file.
    main(doc, op)
