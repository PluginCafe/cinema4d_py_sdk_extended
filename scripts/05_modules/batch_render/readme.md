# Batch Render

The batch renderer allows to organize multiple rendering jobs in a render queue.

Classic API:
- **c4d.documents.BatchRender**: *Represents the batch renderer.*

## Examples

### batchrender_adds_document

    Adds all Cinema 4D files from a selected folder to the render queue.

### batchrender_loops_queue_r13

    Loops over all jobs of the render queue.
    Prints the path if the jobs is not yet render.
