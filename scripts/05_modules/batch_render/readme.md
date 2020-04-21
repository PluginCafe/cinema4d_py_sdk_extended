# Batch Render

The batch renderer allows to organize multiple rendering jobs in a render queue.

Classic API:
- **c4d.documents.BatchRender**: *Represents the batch renderer.*

## Examples


### batchrender_adds_document
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Adds all Cinema 4D files from a selected folder to the render queue.

### batchrender_loops_queue_r13
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Loops over all jobs of the render queue.
    Prints the path if the jobs is not yet render.
