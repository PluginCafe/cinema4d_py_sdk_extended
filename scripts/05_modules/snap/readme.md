# Snap Engine

The snap module lets you access to the snap settings, quantifying options, workplane etc.

Classic API:
- **c4d.modules.snap**: *The module which provides static methods to use the Snap Engine.*

## Examples

### snap_enable_quantize
Version: R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Enables the quantize if it's not already the case.
    Defines quantize Move and Scale step.

### snap_enable_snapping_3d_point
Version: R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Enables the snap if it's not already the case.
    Sets it to 3D Type and also to Point mode.
    
### snap_workplane
Version: R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Retrieves the current workplane position and object.
    Locks this workplane so it can't be edited.
