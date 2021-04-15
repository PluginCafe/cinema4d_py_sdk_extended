# Snap Engine

The snap module lets you access to the snap settings, quantifying options, workplane etc.

Classic API:
- **c4d.modules.snap**: *The module which provides static methods to use the Snap Engine.*

## Examples

### snap_enable_quantize

    Enables the quantize if it's not already the case.
    Defines quantize Move and Scale step.

### snap_enable_snapping_3d_point

    Enables the snap if it's not already the case.
    Sets it to 3D Type and also to Point mode.
    
### snap_workplane

    Retrieves the current workplane position and object.
    Locks this workplane so it can't be edited.
