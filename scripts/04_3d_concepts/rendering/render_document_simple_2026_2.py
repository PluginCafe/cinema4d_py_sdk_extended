"""Demonstrates a simple way to programmatically render a document to either memory or disk.

Note:

    When rendering a document programmatically using #RenderDocument, it will always honor the
    'Save' options set up in the render settings of the document. So, when you render a document
    setup to render a 100 frames animation, saved as an MP4 video, the #RenderDocument call
    will render all 100 frames and save them as an MP4 video to disk.

    But the direct in memory result of #RenderDocument will always be a single frame bitmap, 
    representing the last frame rendered. You can also manually save that bitmap to disk in any
    format you like, independent of the render settings of the document. This is what this example
    demonstrates.

This example contrasted to the more complex example `render_document_complex_2026_2.py which avoids 
automatism in favour of having more control over the rendering process.
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
op: c4d.BaseObject | None  # The primary selected object in `doc`. Can be `None`.

@mxutils.SET_STATUS("Rendering document to memory ...", doSpin=True)
def RenderToPictureViewer(doc: c4d.documents.BaseDocument, settings: c4d.BaseContainer) -> None:
    """Renders the given document and displays the result in the picture viewer.

    Args:
        doc (c4d.documents.BaseDocument): The document to render.
    """
    # Allocate the bitmap to render into. Using #AllocateRenderBitmap takes care for us in setting
    # up the bitmap correctly according to the render settings.
    bmp: c4d.bitmaps.MultipassBitmap = mxutils.CheckType(c4d.bitmaps.AllocateRenderBitmap(settings))

    # Now we are going to render the document into #bmp with the intention to use this bitmap in 
    # memory only. We cold also save it to disk afterwards, but would then have to follow what the
    # more complex example does to correctly bake OCIO data into the image. The flag AUTO_SETUP is
    # an alias for OCIO_RAW_RENDERING | EXTERNAL and ensures that the document will be rendered with
    # the correct rendering engine, highest quality, and correct OCIO handling.
    if c4d.documents.RenderDocument(
        doc, settings, bmp, c4d.RENDERFLAGS_AUTO_SETUP) != c4d.RENDERRESULT_OK:
        raise RuntimeError("Rendering failed.")

    # Display the rendered image in the picture viewer.
    c4d.bitmaps.ShowBitmap(bmp, "AUTO_SETUP Rendered Image")


@mxutils.SET_STATUS("Rendering document to disk ...", doSpin=True)
def RenderToDisk(doc: c4d.documents.BaseDocument, settings: c4d.BaseContainer) -> None:
    """Renders the given document and saves the result to disk.

    Args:
        doc (c4d.documents.BaseDocument): The document to render.
    """
    # Allocate the bitmap to render into.
    bmp: c4d.bitmaps.MultipassBitmap = mxutils.CheckType(c4d.bitmaps.AllocateRenderBitmap(settings))

    # We render the document again, but this time we also pass the flag OCIO_BAKE_RENDERING. It will
    # cause RenderDocument to bake down any OCIO color profile data into the output image as Cinema
    # 4D would according to the render settings before saving an image to disk. You should only use
    # this flag when you intend to save the image to disk, as it can discard high dynamic range
    # data, when the render output settings (everything below 32-bit/channel) demand so.
    flags = c4d.RENDERFLAGS_AUTO_SETUP | c4d.RENDERFLAGS_OCIO_BAKE_RENDERING
    if c4d.documents.RenderDocument(doc, settings, bmp, flags) != c4d.RENDERRESULT_OK:
        raise RuntimeError("Rendering failed.")

    # Save the baked image to disk. The conversion from RDATA_FORMATDEPTH to SAVEBIT is
    # unfortunately something we still must do manually. What we are doing, is effectively copying
    # what the user setup as the bits per channel in the render settings and translate that to a
    # bit depth for our PSD output. So, when the user set up an 8bit rendering, we save a PSD with
    # 8bit channels, when the user set up 16bit, we save a PSD with 16bit channels, and when the user
    # set up 32bit, we save a PSD with 32bit channels.
    formatDepth: int = settings.GetInt32(c4d.RDATA_FORMATDEPTH)
    savebit: int = (c4d.SAVEBIT_USE16BITCHANNELS if formatDepth == c4d.RDATA_FORMATDEPTH_16 else
                    c4d.SAVEBIT_USE32BITCHANNELS if formatDepth == c4d.RDATA_FORMATDEPTH_32 else
                    c4d.SAVEBIT_NONE)
    filePath: str = os.path.join(c4d.storage.GeGetC4DPath(c4d.C4D_PATH_DESKTOP), 
                                 "sdk_render_document_simple.psd")
    if bmp.Save(filePath, c4d.FILTER_PSD, None, savebit) != c4d.IMAGERESULT_OK:
        raise RuntimeError("Failed to save rendered image to disk.")
    
    print(f"Saved rendered image to: {filePath}")
    
    # We can also still display this image in the Picture Viewer. The difference to the other 
    # example is that this image will have been stripped of all OCIO color profile data, and will be
    # an image holding data in the image color profile set up in the render settings (usually sRGB 
    # 2.2).
    c4d.bitmaps.ShowBitmap(bmp, "AUTO_SETUP | OCIO_BAKE_RENDERING Rendered Image")


@mxutils.SET_STATUS("Rendering document ...", doSpin=True)
def main() -> None:
    """Called by Cinema 4D when the script is being executed.
    """
    # When we render a document programmatically using #RenderDocument, we always need to provide
    # render settings in addition to the document to render. Often we want to render the document
    # with slightly different settings than what the user has set up in the render settings itself.
    # It is therefore common practice to clone the current render settings of the document, so that
    # the user settings are not modified.
    renderData: c4d.documents.RenderData = doc.GetActiveRenderData()
    renderContainerCopy: c4d.BaseContainer = mxutils.CheckType(
        renderData.GetDataInstance().GetClone(c4d.COPYFLAGS_NONE))
    
    # Make sure we are rendering the current frame only, so that this example does not run too long.
    renderContainerCopy[c4d.RDATA_FRAMESEQUENCE] = c4d.RDATA_FRAMESEQUENCE_CURRENTFRAME
    
    # Now render the document with the intent to obtain a bitmap that is used in memory only. This
    # could for example be for displaying it in the Picture Viewer, a custom dialog, or as icon/
    # bitmap data somewhere else.
    RenderToPictureViewer(doc, renderContainerCopy)

    # Now render the document with the intent to save the result to disk.
    RenderToDisk(doc, renderContainerCopy)

if __name__ == '__main__':
    main()