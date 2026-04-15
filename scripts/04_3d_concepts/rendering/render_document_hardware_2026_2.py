"""Demonstrates how carry out a 'hardware preview' rendering, i.e., a rendering of what is shown
in the viewport using the hardware renderer.

This example is not particularly complex when you have already understood the other examples, but
it is a common use case, so it is worth having a dedicated example for it.
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2026 MAXON Computer GmbH"
__date__ = "08/01/2026"
__license__ = "Apache-2.0 License"
__version__ = "2026.2.0"

import c4d
import mxutils

import os

doc: c4d.documents.BaseDocument  # The currently active document.

@mxutils.SET_STATUS("Rendering document ...", doSpin=True)
def main() -> None:
    """Called by Cinema 4D when the script is being executed.
    """
    # Get a copy of the active render settings of the document.
    settings: c4d.BaseContainer = mxutils.CheckType(
        doc.GetActiveRenderData().GetDataInstance().GetClone(c4d.COPYFLAGS_NONE))
    
    # Set the engine to 'Hardware Preview', i.e., viewport renderer of Cinema 4D.
    settings[c4d.RDATA_RENDERENGINE] = c4d.RDATA_RENDERENGINE_PREVIEWHARDWARE

    # Render the document using the hardware preview engine into a bitmap.
    bmp: c4d.bitmaps.MultipassBitmap = mxutils.CheckType(c4d.bitmaps.AllocateRenderBitmap(settings))
    if c4d.documents.RenderDocument(
        doc, settings, bmp, c4d.RENDERFLAGS_AUTO_SETUP) != c4d.RENDERRESULT_OK:
        raise RuntimeError("Rendering failed.")

    # Display the rendered image in the picture viewer.
    c4d.bitmaps.ShowBitmap(bmp, "Hardware Preview Rendered Image")

if __name__ == '__main__':
    main()