"""Demonstrates to manipulate the file outputs of a batch render post process once the rendering
has finished.

In this example we render the active document, wait for the rendering to finish, and then rename
the output files by stripping away the frame counter postfix.

Note:

    This code example expects to be run with a document that has been saved and has valid render
    settings with an output path that includes a frame counter token, e.g., "output_#frame_".
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2026 MAXON Computer GmbH"
__date__ = "08/01/2026"
__license__ = "Apache-2.0 License"
__version__ = "2026.2.0"

import c4d
import os
import re
import time

doc: c4d.documents.BaseDocument # The active document.

def RunBatchRenderJob(doc: c4d.documents.BaseDocument) -> tuple[str, str]:
    """Renders the passed document with the render queue.

    Returns the output path and file name pattern as defined in the render settings of the document.
    This function is blocking, i.e., while it is rendering, you will not be able to interact with
    Cinema 4D. This could be changed, but doing this would be up to you.

    Args:
        doc: The document to render.

    Raises:
        RuntimeError: On invalid arguments and failure to operate the render queue.

    Returns:
        The tuple (output directory, render_filename_pattern).
    """
    # Get out when #doc is not a document, has not been saved yet, or the batch renderer is already
    # running. You could also stop an ongoing rendering but I did not.
    if not isinstance(doc, c4d.documents.BaseDocument) or doc.GetDocumentPath() == "":
        raise RuntimeError(f"Invalid document: {doc}")

    batchRender: c4d.documents.BatchRender = c4d.documents.GetBatchRender()
    if batchRender.IsRendering():
        raise RuntimeError(f"Batch renderer is running.")

    # Disable all render jobs which are at the moment in the queue.
    for i in range(batchRender.GetElementCount()):
        batchRender.EnableElement(i, False)

    # Get the path of the passed document file and render output path from the active render settings
    # of the document.
    filePath: str = os.path.join(doc.GetDocumentPath(), doc.GetDocumentName())
    rdata: c4d.documents.RenderData = doc.GetActiveRenderData()
    renderPath: str = rdata[c4d.RDATA_PATH]

    # A render path can come in three forms and we must figure out where the absolute path
    # of the renders is without the file name with tokens.
    #
    #   1. An absolute path, e.g., c:\blah\blah\myRender_#camera_
    #   2. A path relative to the document, e.g., output\myRender_#camera_
    #   3. A file name to the document, e.g., myRender_#camera_

    # Split the path and file name component of #renderPath, and make the renderPath absolute in
    # relation to the document.
    renderPath, renderName = os.path.split(renderPath)
    if not os.path.isabs(renderPath):
        renderPath = os.path.normpath(os.path.join(doc.GetDocumentPath(), renderPath))

    # Add the job at the top, turn on the spin-indicator in the status bar, and start the rendering.
    if not batchRender.AddFile(filePath, 0):
        raise RuntimeError(f"Could not add render job for file: {filePath}")
    
    c4d.StatusSetSpin()
    batchRender.SetRendering(c4d.BR_START)

    # Wait for the render to finish, this a blocking way to implement it, i.e., you will not be
    # able to interact with Cinema 4D until the render has finished. There are more fancy ways to
    # do this with threads which are not blocking, but doing this would be up to you. We wait for a
    # second so that we do not bombard the renderer with IsRendering() polling.
    while batchRender.IsRendering():
        time.sleep(1)

    # The rendering is done, clear the status bar and return the output path and filename pattern.
    c4d.StatusClear()
    return renderPath, renderName

def RenameFiles(path: str, namePattern: str) -> None:
    """Renames files #path by stripping away the frame counter postfix.

    This could be done much more elaborately using the #namePattern argument. I did not do this here.

    Args:
        path: The path to inspect and rename files in. No recursion will happen, i.e., only files
         in #path will be renamed, not files in #path/foo/ for example.
        namePattern: The file name as defined in the render settings of the document, e.g., 
         foo_#frame_1234. Not used here.
    """
    if not os.path.exists(path):
        raise RuntimeError(f"'{path}' does not exist.")
    
    # A regular expression to match three or four digit frame counter at the end of a file name.
    pattern: re.Pattern = re.compile(r"\d\d\d\d?$")

    # Iterate over all files in #path and rename them.
    for oldName in os.listdir(path):
        oldPath: str = os.path.join(path, oldName)
        if not os.path.isfile(oldPath):
            continue
        
        # Split the file name and extension and test if the file name matches #pattern.
        name, extension = os.path.splitext(oldName)
        if not pattern.search(name):
            continue
        
        # Strip away the frame counter part of the name and build a new full file path.
        newName: str = pattern.sub("", name) + extension
        newPath: str = os.path.join(path, newName)

        # Rename the file or raise an error when lack access rights or such file does already exist.
        try:
            os.rename(oldPath, newPath)
        except Exception as error:
            print (f"Stepping over file access error: {error}")

        print (f"Renamed '{oldName}' to '{newName}'.")

def main():
    """Runs the example.
    """
    result: tuple[str, str] = RunBatchRenderJob(doc)
    RenameFiles(*result)


if __name__ == "__main__":
    main()
