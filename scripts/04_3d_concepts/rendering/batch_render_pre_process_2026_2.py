"""Demonstrates how to pre-process multiple documents before adding them to the batch renderer
for rendering.

In this example we load all .c4d files from a selected directory, modify their render settings
to use a specific render data (or a fallback one when not present), save them as temporary files,
and add them to the batch renderer for rendering.
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2026 MAXON Computer GmbH"
__date__ = "08/01/2026"
__license__ = "Apache-2.0 License"
__version__ = "2026.2.0"

import c4d
import os
import time

import c4d
import mxutils

import os
import typing
import time

def ModifyDocument(doc: c4d.documents.BaseDocument, renderDataTargetName: str,
                   fallbackRenderData: typing.Optional[c4d.documents.RenderData] = None) -> None:
    """Modifies a document according to what you want to do.

    This is just an example, the function could do anything, we just switch the active render data
    to the one named #renderDataTargetName, or use #fallbackRenderData when that name is not present.

    Args:
        doc: The document to modify.
        renderDataTargetName: The name of the render data to load in the document.
        fallbackRenderData: The render data to use when #renderDataTargetName is not present. Will
        be ignored when None. Defaults to None.
    """
    mxutils.CheckType(doc, c4d.documents.BaseDocument)

    # Loop over all render data in the document to find the one we want to set active.
    for renderData in mxutils.IterateTree(doc.GetFirstRenderData(), True):
        if renderData.GetName() == renderDataTargetName:
            doc.SetActiveRenderData(renderData)
            return

    # When we reach this point it means that #renderDataTargetName was not contained in #doc, so we
    # must use #fallbackRenderData when provided.
    if fallbackRenderData:
        clone: c4d.documents.RenderData = fallbackRenderData.GetClone(c4d.COPYFLAGS_0)
        doc.InsertRenderDataLast(clone)
        doc.SetActiveRenderData(clone)
    else:
        raise RuntimeError(f"Document does not contain render data named "
                           f"'{renderDataTargetName}' and no fallback provided.")


def main() -> None:
    """Called by Cinema 4D when the script is being executed.
    """
    # Let the user select a directory to scan for documents to modify and batch render.
    directory: str = c4d.storage.LoadDialog(
        title="Please select the scene directory", flags=c4d.FILESELECT_DIRECTORY)
    if directory is None:
        return

    # Our script will look for a render data named "My Render Setting.1" in each document. When not
    # found, it will use some fallback render data we create below (it just enables the Hardware 
    # Preview engine and sets a custom output path pattern on a per document basis).
    targetRenderSettings: str = "My Render Setting.1"
    batchRenderFiles: list[str] = []

    # Walk the directory the user selected for .c4d files.
    for root, _, files in os.walk(directory):
        for f in files:
            if not f.endswith("c4d"):
                continue
            
            # Load the file into a Cinema 4D document and make up a new path for the modified 
            # document.
            filePath: str = os.path.join(root, f)
            doc: c4d.BaseDocument = c4d.documents.LoadDocument(filePath, c4d.SCENEFILTER_NONE)
            if not isinstance(doc, c4d.documents.BaseDocument):
                raise OSError(f"Failed loading into a c4d document: '{filePath}'")

            name: str = os.path.splitext(doc.GetDocumentName())[0]
            newPath: str = os.path.join(doc.GetDocumentPath(), f"modified_{name}.c4d")

            # doc could not contain #targetRenderSettings, so we build some fallback data to use
            # instead. They could also be loaded from another document, etc.
            fallback: c4d.documents.RenderData = c4d.documents.RenderData()
            fallback[c4d.RDATA_RENDERENGINE] = c4d.RDATA_RENDERENGINE_PREVIEWHARDWARE
            fallback[c4d.RDATA_SAVEIMAGE] = True
            fallback[c4d.RDATA_PATH] = f"render_{name}"
            fallback[c4d.RDATA_FORMAT] = c4d.FILTER_PNG

            # Modify #doc to whatever you want to do.
            ModifyDocument(doc, targetRenderSettings, fallback)

            # Save the document and append the file to the to be rendered files.
            if not c4d.documents.SaveDocument(doc, newPath, c4d.SAVEDOCUMENTFLAGS_NONE, 
                                              c4d.FORMAT_C4DEXPORT):
                raise OSError(f"Could not save {doc} to '{newPath}'.")
            batchRenderFiles.append(newPath)


    # Get the batch renderer.
    batchRender: c4d.documents.BatchRender = c4d.documents.GetBatchRender()

    # Disable all render jobs which are at the moment in the queue and not related to our task.
    for i in range(batchRender.GetElementCount()):
        batchRender.EnableElement(i, False)

    # Add our modified documents to the batch render queue.
    for i, file in enumerate(batchRenderFiles):
        batchRender.AddFile(file, 0)

    # Carry out the batch rendering. This is a blocking call, so while rendering you will not be 
    # able to interact with Cinema 4D. You could also implement this in a non-blocking way using
    # threads, but that would be up to you. Alternatively, we could also just open the batch render
    # dialog so that the user can start the rendering manually (using #batchRender.Open()).
    c4d.StatusSetSpin()
    batchRender.SetRendering(c4d.BR_START)

    # Wait for the render to finish, this a blocking way to implement it, i.e., you will not be
    # able to interact with Cinema 4D until the render has finished. There are more fancy ways to
    # do this with threads which are not blocking, but doing this would be up to you. We wait for a
    # second so that we do not bombard the renderer with IsRendering() polling.
    while batchRender.IsRendering():
        time.sleep(1)

    # The rendering is done, clear the status bar and return the output path and filename pattern.
    batchRender.SetRendering(c4d.BR_STOP)
    c4d.StatusClear()

    batchRender.Open()

    # FInally, once done we can clean up ourself and remove the modified documents.
    for file in batchRenderFiles:
        try:
            os.remove(file)
            print(f"Removed temporary file: {file}")
        except Exception as e:
            print(f"Could not remove temporary file '{file}': {e}")

    print("Batch rendering of modified documents completed.")


if __name__ == '__main__':
    main()
