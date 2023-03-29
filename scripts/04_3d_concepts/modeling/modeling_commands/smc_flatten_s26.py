#coding: utf-8
"""Demonstrates how to execute the 'Flatten' tool.

Invokes 'Flatten' tool on the currently selected object for its currently selected polygons in 
the active document via `SendModelingCommand`.

Topics:
    * The 'Flatten' tool
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

def main(doc: c4d.documents.BaseDocument, op: typing.Optional[c4d.BaseObject]) -> None:
    """Runs the example.

    Args:
        doc: The active document.
        op: The selected object in #doc. Can be #None.
    """
    if not isinstance(op, c4d.BaseObject):
        raise TypeError(f"Please select an object.")

    # The settings of the 'Flatten' tool.
    bc = c4d.BaseContainer()
    # The strength of the operation set to 100%.
    bc[c4d.MDATA_FLATTEN_WEIGHT] = 1.0
    # Use the "Best Fit" mode.
    bc[c4d.MDATA_FLATTEN_METHOD] = c4d.MDATA_FLATTEN_METHOD_BESTFIT
    # The position of the plane to project into set to 50%, i.e., half way between the min and max
    # of the bounding box on the y-axis (of the selected polygons).
    bc[c4d.MDATA_FLATTEN_PLANEPOSITION] = .5

    # Execute the command with the undo flag set. It can also be executed in point and edge mode.
    res = c4d.utils.SendModelingCommand(command=c4d.ID_MODELING_FLATTEN_TOOL, 
                                        list=[op], 
                                        mode=c4d.MODELINGCOMMANDMODE_POLYGONSELECTION, 
                                        bc=bc, 
                                        doc=doc, 
                                        flags=c4d.MODELINGCOMMANDFLAGS_CREATEUNDO)
    if not res:
        raise RuntimeError(f"Modelling command failed for {op}.")

    # Inform Cinema 4D that the document has been modified.
    c4d.EventAdd()


if __name__ == '__main__':
    # #doc and #op are predefined module attributes as defined at the top of the file.
    main(doc, op)
