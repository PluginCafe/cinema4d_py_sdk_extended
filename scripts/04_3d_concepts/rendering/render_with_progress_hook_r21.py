"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Render the current document with a progress hook to get notified about the current rendering progress.

Class/method highlighted:
    - c4d.bitmaps.MultipassBitmap
    - c4d.documents.RenderDocument()

Compatible:
    - Win / Mac
    - R21, S22, R23
"""
import c4d


def PythonCallBack(progress, progress_type):
    """
    Function passed in RenderDocument. It will be called automatically by Cinema 4D with the current render progress.

    :param progress: The percent of the progress for the current step
    :type progress: float
    :param progress_type: The Main part of the current rendering step
    :type progress_type: c4d.RENDERPROGRESSTYPE
    """
    text = str()

    if progress_type == c4d.RENDERPROGRESSTYPE_BEFORERENDERING:
        text = "Before Rendering"

    elif progress_type == c4d.RENDERPROGRESSTYPE_DURINGRENDERING:
        text = "During Rendering"

    elif progress_type == c4d.RENDERPROGRESSTYPE_AFTERRENDERING:
        text = "After Rendering"

    elif progress_type == c4d.RENDERPROGRESSTYPE_GLOBALILLUMINATION:
        text = "GI"

    elif progress_type == c4d.RENDERPROGRESSTYPE_QUICK_PREVIEW:
        text = "Quick Preview"

    elif progress_type == c4d.RENDERPROGRESSTYPE_AMBIENTOCCLUSION:
        text = "AO"

    # Prints to the console the current progress
    print("ProgressHook called [{0} / p: {1}]".format(text, progress * 100.0))


def PythonWriteCallBack(mode, bmp, fn, mainImage, frame, renderTime, streamnum, streamname):
    """
    Function passed in RenderDocument.
    It will be called automatically by Cinema 4D when the file rendered file should be saved.

    :param mode: The write mode.
    :type mode: c4d.WRITEMODE
    :param bmp: The bitmap written to.
    :type bmp: c4d.bitmaps.BaseBitmap
    :param fn: The path where the file should be saved.
    :type fn: str
    :param mainImage: True for main image, otherwise False.
    :type mainImage: bool
    :param frame: The frame number.
    :type frame: int
    :param renderTime: The bitmap frame time.
    :type renderTime: int
    :param streamnum: The stream number.
    :type streamnum: int
    :param streamname: The stream name.
    :type streamname: str
    """
    text = str()

    if mode == c4d.WRITEMODE_STANDARD:
        text = "Standard"

    elif mode == c4d.WRITEMODE_ASSEMBLE_MOVIE:
        text = "Assemble Movie"

    elif mode == c4d.WRITEMODE_ASSEMBLE_SINGLEIMAGE:
        text = "Assemble single image"

    print("ProgressWriteHook called [{0} / p: {1}]".format(text, renderTime))


def main():
    # Retrieves the current active render settings
    rd = doc.GetActiveRenderData()

    # Creates a Multi Pass Bitmaps that will store the render result
    bmp = c4d.bitmaps.MultipassBitmap(int(rd[c4d.RDATA_XRES]), int(rd[c4d.RDATA_YRES]), c4d.COLORMODE_RGB)
    if bmp is None:
        raise RuntimeError("Failed to create the bitmap.")

    # Adds an alpha channel
    bmp.AddChannel(True, True)

    # Renders the document
    if c4d.documents.RenderDocument(doc, rd.GetData(), bmp, c4d.RENDERFLAGS_EXTERNAL, prog=PythonCallBack,
                                    wprog=PythonWriteCallBack) != c4d.RENDERRESULT_OK:
        raise RuntimeError("Failed to render the temporary document.")

    # Displays the render in the Picture Viewer
    c4d.bitmaps.ShowBitmap(bmp)


if __name__ == "__main__":
    main()
