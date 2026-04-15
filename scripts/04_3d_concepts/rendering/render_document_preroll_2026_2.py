"""Demonstrates how to render document from or at a given frame after prerolling it.

In general, one can just set the render document to the desired frame and render it. But modern
documents contain more and more simulation data such as hair, particles, cloth, fluids, etc., 
whose output depends on the state of the simulation at the given frame. Unless the simulation
has been cached, just jumping to a given frame and rendering it will not yield the expected results.

This example demonstrates how to 'preroll' the document to the desired frame before rendering it,
so that all simulations are in the correct state.

Cinema 4D also has a the option 'Force Pre-Roll' in its render settings (defined as 
`RDATA_FORCE_PREROLL`), which will automatically preroll the document when rendering. The advantage 
of manual prerolling is that you can preroll without rendering, and you have more control over how 
the prerolling is done (for example, you can skip evaluating certain components if you know they 
are not needed).
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2026 MAXON Computer GmbH"
__date__ = "08/01/2026"
__license__ = "Apache-2.0 License"
__version__ = "2026.2.0"

import c4d
import mxutils

doc: c4d.documents.BaseDocument  # The currently active document.

@mxutils.SET_STATUS("Prerolling document ...", doSpin=True)
def PrerollDocumentToFrame(
        doc: c4d.documents.BaseDocument, frame: int, forceFromStart: bool = False) -> None:
    """Sets the given document to the specified frame and forces an evaluation of all simulation
    up to that frame.

    Note:

        Prerolling a document can be an EXTREMELY expensive operation, depending on the complexity
        of the scene. When you have a scene that costs 30 minutes to simulate up to frame 100, and
        you want to preroll from frame 0 to frame 100, this will take 30 minutes.

    Args:
        doc (c4d.documents.BaseDocument): The document to preroll.
        frame (int): The frame to preroll to.
        forceFromStart (bool, optional): If `True`, forces to preroll from the first frame of the
         document. If `False` and applicable, the preroll will start from the current frame of
         the document.
    """
    mxutils.CheckType(doc, c4d.documents.BaseDocument)
    targetFrame: int = int(frame)
    
    # Get the current, min and max frame of the document.
    fps: int = doc.GetFps()
    currentFrame: int = int(doc.GetTime().GetFrame(fps))
    minFrame: int = int(doc.GetMinTime().GetFrame(fps))
    maxFrame: int = int(doc.GetMaxTime().GetFrame(fps))

    if targetFrame < minFrame or targetFrame > maxFrame:
        raise ValueError(
            f"Target frame {targetFrame} is out of document frame range [{minFrame}, {maxFrame}].")
    
    # Now we are going to preroll and there are two scenarios: (A) the target frame lies before the
    # current frame, in that case we have to preroll from the first frame up to the target frame. (B) 
    # the target frame lies after the current frame, in that case we can just preroll from the current
    # frame to the target frame (unless forceFromStart is True).
    startFrame: int = minFrame if (targetFrame < currentFrame or forceFromStart) else currentFrame
    
    # Prerolling means that we iteratively build scene data frame by frame up the target frame. 
    # In Cinema 4D, this is done by calling SetTime() and ExecutePasses() on the document for each
    # frame in the preroll range.
    for frame in range(startFrame, targetFrame + 1):
        # Set the document time to the current preroll frame.
        doc.SetTime(c4d.BaseTime(frame, fps))
        print(f"Prerolling to frame {frame}...")
        # Force an evaluation of the document at the new time, so that all scene data is updated.
        # Here is room for optimization when we do not need all scene data, such as animations or
        # expressions (what the user calls 'tags'). You almost always want to evaluate caches which
        # also make up most of the cost. Caches are things like geometry generators and the many
        # simulation systems Cinema 4D has (simulations are usually not at all or only weakly affected
        # animations). Disabling expressions can also have side effects, as scene elements can rely
        # on hidden tags to compute their state.
        if not doc.ExecutePasses(bt=None, animation=True, expressions=True, caches=True, 
                                 flags=c4d.BUILDFLAGS_NONE):
            raise RuntimeError(f"Failed to preroll document to frame {frame}.")

    # For the last frame, we should execute the passes twice, so that systems can settle. This is 
    # required because Cinema 4D scenes can contain circular dependencies, and one needs then more 
    # than one pass to reach a stable state then.
    if not doc.ExecutePasses(bt=None, animation=True, expressions=True, caches=True, 
                             flags=c4d.BUILDFLAGS_NONE):
        raise RuntimeError(f"Failed to preroll document to frame {targetFrame}.")

def main() -> None:
    """Called by Cinema 4D when the script is being executed.
    """
    # We just grab the middle frame of the document.
    minFrame: int = int(doc.GetMinTime().GetFrame(doc.GetFps()))
    maxFrame: int = int(doc.GetMaxTime().GetFrame(doc.GetFps()))
    targetFrame: int = (minFrame + maxFrame) // 2

    # We preroll the document to the target frame.
    PrerollDocumentToFrame(doc, targetFrame, forceFromStart=True)

    # And then just render only that frame.
    c4d.gui.StatusSetText(f"Rendering frame {targetFrame} after prerolling...")

    data: c4d.BaseContainer = mxutils.CheckType(
        doc.GetActiveRenderData().GetDataInstance().GetClone(c4d.COPYFLAGS_NONE))
    data[c4d.RDATA_FRAMESEQUENCE] = c4d.RDATA_FRAMESEQUENCE_CURRENTFRAME
    bmp: c4d.bitmaps.MultipassBitmap = mxutils.CheckType(c4d.bitmaps.AllocateRenderBitmap(data))

    if c4d.documents.RenderDocument(doc, data, bmp, c4d.RENDERFLAGS_AUTO_SETUP) != c4d.RENDERRESULT_OK:
        raise RuntimeError("Rendering failed.")
    
    c4d.bitmaps.ShowBitmap(bmp, f"Rendered Frame {targetFrame} after Prerolling")
    c4d.gui.StatusClear()


if __name__ == '__main__':
    main()
    
