"""Demonstrates the details and manual handling of a programmatic rendering process.

Note:

    When rendering a document programmatically using #RenderDocument, it will always honor the
    'Save' options set up in the render settings of the document. So, when you render a document
    setup to render a 100 frames animation, saved as an MP4 video, the #RenderDocument call
    will render all 100 frames and save them as an MP4 video to disk.

    But the direct in memory result of #RenderDocument will always be a single frame bitmap, 
    representing the last frame rendered. You can also manually save that bitmap to disk in any
    format you like, independent of the render settings of the document. This is what this example
    demonstrates.

Please refer to the simpler example `render_document_simple_2026_2.py` for a more beginner friendly 
explanation of the rendering process.
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

def ProgressHook(percent: float, progressType: int) -> None:
    """Realizes a progress hook to monitor the rendering process.

    The plain progress hook is the main way to monitor the rendering process when rendering
    programmatically. It is called periodically during the rendering process with the current
    progress in percent and the stage of the rendering process.

    Note that while the rendering itself is not blocking (the rendering itself happens in a separate
    thread), our call to #RenderDocument is blocking, and so is the progress hook. This means that
    when we print to the console in the progress hook, we will not see any output until the rendering
    is finished. One could decouple the #RenderDocument call into a separate thread and then have
    from the main thread something periodically checking that render thread (which would be using
    a progress hook to record its progress), and with that have a continuous GUI updates of a render
    progress. But that drive up the complexity of the example quite a bit, so we are not doing that 
    here.
    """
    # The progressType indicates in which stage of the rendering process we currently are and the
    # percent indicates how far we are in that stage.
    if progressType == c4d.RENDERPROGRESSTYPE_BEFORERENDERING:
        print(f"Initializing rendering: {percent*100:.2f}%")
    elif progressType == c4d.RENDERPROGRESSTYPE_DURINGRENDERING:
        print(f"Rendering in progress: {percent*100:.2f}%")
    elif progressType == c4d.RENDERPROGRESSTYPE_AFTERRENDERING:
        print(f"Finalizing rendering: {percent*100:.2f}%")
    elif progressType == c4d.RENDERPROGRESSTYPE_CANCELLED:
        print(f"Rendering cancelled: {percent*100:.2f}%")
    # The following progress types are only supported by the standard and physical render engines.
    elif progressType == c4d.RENDERPROGRESSTYPE_GLOBALILLUMINATION:
        print(f"Calculating Global Illumination: {percent*100:.2f}%")
    elif progressType == c4d.RENDERPROGRESSTYPE_AMBIENTOCCLUSION:
        print(f"Calculating Ambient Occlusion: {percent*100:.2f}%")
    elif progressType == c4d.RENDERPROGRESSTYPE_QUICK_PREVIEW:
        print(f"Calculating Quick Preview: {percent*100:.2f}%")
    return True

def WriteProgressHook(
        mode: int, bmp: c4d.bitmaps.BaseBitmap, fileName: str, isMainImage: bool, frame: int,
        renderTime: int, streamNumber: int, streamName: int) -> None:
    """Realizes a write progress hook to monitor the writing of image data to disk.

    The write progress hook is called periodically during the writing of image data to disk. It is
    rather rare the one has to hook into the write progress. A write progress hook is therefor only
    called when the render settings enable saving to disk.

    Write progress hooks are read-only regarding the image data, manipulating the passed bitmap
    will have no effect as to what is written to disk. But we could manipulate the bitmap and save 
    it ourself to disk in a different location or format.
    """
    print(f"{frame} frame is written to disk: '{fileName}' (stream: {streamNumber} - '{streamName}')")

@mxutils.SET_STATUS("Rendering document ...", doSpin=True)
def main() -> None:
    """Called by Cinema 4D when the script is being executed.
    """
    # Get the document container and a copy of the active render settings container.
    docSettings: c4d.BaseContainer = mxutils.CheckType(doc.GetDataInstance())
    renderSettings: c4d.BaseContainer = mxutils.CheckType(
        doc.GetActiveRenderData().GetDataInstance().GetClone(c4d.COPYFLAGS_NONE))
    isOcioDocument: bool = (docSettings.GetBool(c4d.DOCUMENT_COLOR_MANAGEMENT) == 
                            c4d.DOCUMENT_COLOR_MANAGEMENT_OCIO)
    
    # Make sure we are rendering the current frame only, so that this example does not run too long.
    renderSettings[c4d.RDATA_FRAMESEQUENCE] = c4d.RDATA_FRAMESEQUENCE_CURRENTFRAME
    
    # When the document is an OCIO document, we must disable the #RDATA_BAKE_OCIO_VIEW_TRANSFORM_RENDER
    # flag to ensure the rendering correctly outputs data in render space colors. This flag is
    # different from the #RDATA_BAKE_OCIO_VIEW_TRANSFORM flag which is shown in the render settings
    # when using 32-bit float formats.
    if isOcioDocument:
        renderSettings.SetBool(c4d.RDATA_BAKE_OCIO_VIEW_TRANSFORM_RENDER, False)

    # Now manually setup the render bitmap. For modern Cinema 4D instances, the rendering pretty 
    # much always happens in 32-bit float precision, no matter what the user set in the render 
    # settings.
    xRes: int = int(renderSettings[c4d.RDATA_XRES_VIRTUAL] or renderSettings[c4d.RDATA_XRES])
    yRes: int = int(renderSettings[c4d.RDATA_YRES_VIRTUAL] or renderSettings[c4d.RDATA_YRES])
    bmp: c4d.bitmaps.BaseBitmap = mxutils.CheckType(
        c4d.bitmaps.MultipassBitmap(xRes, yRes, c4d.COLORMODE_RGBf))
    bmp.AddChannel(True, True)

    # Carry out the rendering. We pretty much always want to use the flag #RENDERFLAGS_EXTERNAL as
    # it not only enables the use of third party render engines, but also ensure that scene data
    # is being rebuilt to the highest quality when necessary. We also pass a read and write hook
    # to monitor the rendering process (which only makes partially sense when only rending a single
    # frame, but is included here for completeness).
    renderResult: int = c4d.documents.RenderDocument(
        doc, renderSettings, bmp, c4d.RENDERFLAGS_EXTERNAL, prog=ProgressHook, wprog=WriteProgressHook)
    
    if renderResult != c4d.RENDERRESULT_OK:
        raise RuntimeError(f"Rendering failed with error code: {renderResult}.")

    # We can not simply show the rendered bitmap in the Picture Viewer. This image will be an image
    # in render space colors (assuming we rendered an OCIO document). 
    c4d.bitmaps.ShowBitmap(bmp, f"Rendered Frame {int(doc.GetTime().GetFrame(doc.GetFps()))}")

    # Here you could manipulate the render output in render space colors ... 

    # If we would now try to save this image as is to disk, and the user did not choose a 32-bit 
    # format and disabled #RDATA_BAKE_OCIO_VIEW_TRANSFORM in the render settings, the saved image 
    # would be different from what Cinema 4D would save. because our data is still in (linear) 
    # render space colors and must be baked down to a non-linear representation. This can be done
    # with #BakeOcioViewToBitmap.

    # Get the output depth the user set up in the render settings and convert it to a savebit.
    formatDepth: int = renderSettings.GetInt32(c4d.RDATA_FORMATDEPTH)
    savebit: int = (c4d.SAVEBIT_USE16BITCHANNELS if formatDepth == c4d.RDATA_FORMATDEPTH_16 else
                    c4d.SAVEBIT_USE32BITCHANNELS if formatDepth == c4d.RDATA_FORMATDEPTH_32 else
                    c4d.SAVEBIT_NONE)

    # Bake the bitmap down. #BakeOcioViewToBitmap will return None when no baking was necessary,
    # in which case we just keep our original bitmap.
    if isOcioDocument:
        bmp = c4d.documents.BakeOcioViewToBitmap(bmp, renderSettings, savebit) or bmp

    # Save the (possibly baked) image to disk as a PSD file.
    filePath: str = os.path.join(c4d.storage.GeGetC4DPath(c4d.C4D_PATH_DESKTOP), 
                                 "sdk_render_document_complex.psd")
    if bmp.Save(filePath, c4d.FILTER_PSD, None, savebit) != c4d.IMAGERESULT_OK:
        raise RuntimeError("Failed to save rendered image to disk.")
    
    print(f"Saved rendered image to: {filePath}")

if __name__ == '__main__':
    main()