"""Demonstrates how to manipulate the render settings of a rendering, specifically also the used
render engine.
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
    # This example use the simple workflow to render to memory. See the _simple and _complex for
    # details on how to render manually or to disk.

    # Draw a copy of the active render settings of the document.
    settings: c4d.BaseContainer = mxutils.CheckType(
        doc.GetActiveRenderData().GetDataInstance().GetClone(c4d.COPYFLAGS_NONE))
    
    # Most render settings can be just directly manipulated on the settings container. So, if we
    # wanted to half the render resolution, we could do this:
    settings[c4d.RDATA_XRES] = settings[c4d.RDATA_XRES] / 2
    settings[c4d.RDATA_YRES] = settings[c4d.RDATA_YRES] / 2

    # More complicated can be to change the render engine. The engine is reflected in the 
    # RDATA_RENDERENGINE and we could enable Redshift as the render engine like this, where 
    # #VPrsrenderer is the ID of the Redshift render engine.
    settings[c4d.RDATA_RENDERENGINE] = c4d.VPrsrenderer

    # The issue with this is that for any render engine except Standard/Physical and the Hardware 
    # Preview, this CAN be not enough, as most 'external' render engines (and Redshift counts 
    # in the Cinema API logic as an external render engine) require their own video post effect to
    # be present for the rendering to succeed. The video post effect might already be present when
    # the user has manually switched to that engine before or the engine always injects its video 
    # post effect automatically, but this is not guaranteed. This especially applies when we render 
    # a document that is not that active document or even has been just programmatically
    # created from scratch, as some automatisms will not work there. So, it is better to handle this
    # case explicitly.

    # But this brings up the problem that we cannot only render the document with a copy of the
    # render settings container anymore. Because the video post effects are part of the render data
    # and not part of the data container of the render data. We either have to create a full clone 
    # of the render data and manipulate and insert that into the document, or directly manipulate 
    # the active render data of the document. The former has the advantage that we could remove the
    # extra render data again afterwards to restore the previous state. This example will directly
    # manipulate the active render data for simplicity.

    # Get the active render data of the document.
    renderData: c4d.documents.RenderData = doc.GetActiveRenderData()

    # Set the active render engine to Redshift.
    renderData[c4d.RDATA_RENDERENGINE] = c4d.VPrsrenderer

    # Iterate over all video post effects and remove any effect not compatible with the Redshift 
    # render engine and finally make sure the Redshift video post effect itself is present. We do 
    # not remove the effects in place in the loop, as that would mess up the iteration because nodes
    # effectively work as a linked list.
    removeEffects: list[c4d.documents.BaseVideoPost] = []
    foundRedshiftEffect: bool = False
    for effect in mxutils.IterateTree(renderData.GetFirstVideoPost(), True):
        # This is the Redshift video post effect.
        if effect.GetType() == c4d.VPrsrenderer:
            foundRedshiftEffect = True
            continue
        # This is some effect not compatible with Redshift.
        elif not effect.RenderEngineCheck(c4d.VPrsrenderer):
            removeEffects.append(effect)

    # Remove all the video post effects we marked for removal.
    for effect in removeEffects:
        effect.Remove()

    # And add the Redshift video post effect if it was not found yet. Note that there is no hard
    # guarantee that a render engine uses the same ID for its video post effect as the render 
    # engine ID (VPrsrenderer in this case). But it is a very common convention, check with your
    # render engine vendor for details.
    if not foundRedshiftEffect:
        redshiftEffect: c4d.documents.BaseVideoPost = mxutils.CheckType(
            c4d.documents.BaseVideoPost(c4d.VPrsrenderer))
        renderData.InsertVideoPost(redshiftEffect)

    # Now we can render out document with Redshift.
    settings: c4d.BaseContainer = renderData.GetDataInstance()
    bmp: c4d.bitmaps.MultipassBitmap = mxutils.CheckType(c4d.bitmaps.AllocateRenderBitmap(settings))
    if c4d.documents.RenderDocument(
        doc, renderData.GetDataInstance(), bmp, c4d.RENDERFLAGS_AUTO_SETUP) != c4d.RENDERRESULT_OK:
        raise RuntimeError("Rendering failed.")

    # Display the rendered image in the picture viewer.
    c4d.bitmaps.ShowBitmap(bmp, "Redshift Rendered Image")

if __name__ == '__main__':
    main()