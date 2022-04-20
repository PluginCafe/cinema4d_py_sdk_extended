#coding: utf-8
"""Demonstrates how to execute the 'Edge Smooth' tool.

Invokes 'Edge Smooth' tool on the currently selected object for its currently selected edges in 
the active document via SendModellingCommand.

Topics:
    * The 'Edge Smooth' tool
    * c4d.utils.SendModellingCommand()
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
    if not isinstance(op, c4d.BaseObject):
        raise TypeError(f"Please select an object.")

    # The settings of the 'Edge Smooth' tool.
    bc = c4d.BaseContainer()
    # The smoothing iterations. This is a fairly high value for demonstration purposes.
    bc[c4d.MDATA_EDGESMOOTH_STEPS] = 250

    # Execute the command with the undo flag set. The tool can also be executed in point mode.
    res = c4d.utils.SendModelingCommand(command=c4d.ID_MODELING_EDGESMOOTH_TOOL, 
                                        list=[op], 
                                        mode=c4d.MODELINGCOMMANDMODE_EDGESELECTION, 
                                        bc=bc, 
                                        doc=doc, 
                                        flags=c4d.MODELINGCOMMANDFLAGS_CREATEUNDO)
    if not res:
        raise RuntimeError(f"Modelling command failed for {op}.")

    # Inform Cinema 4D that the document has been modified.
    c4d.EventAdd()


if __name__ == '__main__':
    c4d.CallCommand(13957)  # Clear the console.
    # #doc and #op are predefined module attributes as defined at the top of the file.
    main(doc, op)
