#coding: utf-8
"""Demonstrates how to execute the 'Current State to Object' tool.

Invokes 'Current State to Object' on the currently selected object in the active document via
`SendModelingCommand`. 'Current State to Object' is often the better alternative to evaluating the 
caches of an object or BaseDocument.Polygonize() when a collapsed PointObject representation of a 
generator chain is required.

Topics:
    * The 'Current State to Object' tool
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

    # The settings of 'Current State to Object'. The tool has multiple settings (which are not
    # directly accessible for the user in the app) but none of them are relevant in this example
    # and because of that, the tool container can remain empty.
    bc = c4d.BaseContainer()

    # Execute the command with the undo flag set.
    res = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_CURRENTSTATETOOBJECT, 
                                        list=[op], 
                                        mode=c4d.MODELINGCOMMANDMODE_ALL, 
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
