# LodObject

A LodObject represents a LOD (level of detail) object generator. This generator creates geometry based on various parameters e.g. camera distance.

The LodObject class provides access to the parameters of the dynamically defined levels.

Classic API:
- **c4d.LodObject**: *Represents a LOD (level of detail) object generator.*

## Examples

### lodobject_create

    Creates a new LOD object and adds it to the active BaseDocument.

### lodobject_display

    Configures the display settings for each level of the active LOD object 'op'.

### lodobject_level

    Hides the objects of the active LOD object 'op' current level.

### lodobject_objectlist

    Configures the active LOD object to use "Manual Groups".
    The selected objects referenced in the objects list are moved under the LOD object and are referenced in each group.

### lodobject_parameter

    Checks the current criteria of the active LOD object 'op'.
    If it is "User LOD Level" the current level is set to the maximum level.

### lodobject_simplify

    Configures the active LodObject 'op' to use the "Simplify" mode.
    The first level uses the "Convex Hull" mode, the second the "Null" mode.
    The second level uses the "Simplify" mode and a manual number of levels.
