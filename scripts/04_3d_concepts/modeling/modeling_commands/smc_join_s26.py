#coding: utf-8
"""Demonstrates how to execute the 'Join' tool.

Invokes 'Join' tool on the currently selected objects in the active document via `SendModelingCommand`.

Topics:
    * The 'Join' tool
    * c4d.utils.SendModelingCommand()

Note:
    See `smc_extrude_s26.py` for a more in depth overview of the topic of `SendModelingCommand`.
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

def main(doc: c4d.documents.BaseDocument) -> None:
    """Runs the example.

    Args:
        doc: The active document.
    """
    # Retrieve all directly selected objects.
    objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_NONE)

    # The join tool requires its inputs to be parented to a null object. This implies using a dummy 
    # document as the user could have selected parts of a hierarchy where it would be then ambiguous
    # which parts should be moved where:
    # 
    #   Object 1
    #      Object 1.1 [selected]
    #         Object 1.1.1
    #   Object 2
    #       Object 2.1 [selected]
    #         Object 2.1.1
    #

    # An empty dummy document to carry the command out with.
    temp = c4d.documents.BaseDocument()

    # Insert clones of all input objects under a new null object and insert that null object into
    # the dummy document.
    null = c4d.BaseObject(c4d.Onull)

    for node in objects:
        clone = node.GetClone(c4d.COPYFLAGS_NO_HIERARCHY)
        clone.InsertUnderLast(null)

    temp.InsertObject(null)

    # The settings of the 'Join' tool.
    bc = c4d.BaseContainer()
    # Merge possibly existing selection tags.
    bc[c4d.MDATA_JOIN_MERGE_SELTAGS] = True

    # Execute the Join command in the dummy document.
    res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_JOIN, 
                                        list=[null], 
                                        mode=c4d.MODELINGCOMMANDMODE_ALL, 
                                        bc=bc, 
                                        doc=temp, 
                                        flags=c4d.MODELINGCOMMANDFLAGS_CREATEUNDO)
    if not res:
        raise RuntimeError(f"Modelling command failed for {op}.")

    # The 'Join' command returns its result in the return value of SendModelingCommand()
    joinResult = res[0]
    if not isinstance(joinResult, c4d.BaseObject):
        raise RuntimeError("Unexpected return value for Join tool.")
    
    joinResult.SetName("Join Result (SMC)")
    
    # Insert the joined geometry back into the original document as a new object, wrapping the
    # operation into an undo.
    if not doc.StartUndo():
        raise RuntimeError("Could not open undo stack.")

    doc.InsertObject(joinResult)

    if not doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, joinResult):
        raise RuntimeError("Could not add undo item.")

    if not doc.EndUndo():
        raise RuntimeError("Could not close undo stack.") 

    # Inform Cinema 4D that the document has been modified.
    c4d.EventAdd()


if __name__ == '__main__':
    # #doc is a predefined module attribute as defined at the top of the file.
    main(doc)
