# Animation

Keyframes animation of parameters is organized in tracks, curves and keys.

Classic API:
- **c4d.CTrack**: *Stores the animation datas of a single parameter in multiple CCurves.*
- **c4d.CCurve**: *Represents an animation curve defined by multiple keys.*
- **c4d.Ckey**: *Represents a key of an animation track.*

## Examples

### baseobject_find_best_euler_angle

    Checks the rotation tracks of the active object.

### baseobject_get_vector_curves

    Reads the vector components curves of the active object's rotation track curve.

### baseobject_get_vector_tracks

    Reads the vector components tracks of the active object's position track curve.

### baseobject_quaternion_rotation_mode

    Checks if the active object uses quaternion interpolation.

### baseobject_synchronize_vector_track_keys

    Synchronizes the keys for the tracks of the active cube's "Size" parameter.

### ckey_quaternion_interpolation

    Checks the interpolation of the first key for an object's rotation track.
    If the interpolation is linear (SLERP) it is changed to cubic.

### ctrack_copy

    Copies the position, rotation and animation Tracks (so all Keyframes) from obj1 to obj2.

### ctrack_create_keys

	Creates position Y tracks.
	Adds two keyframes.
	Sets their value and interpolation.

### ctrack_synchronized

    Checks if the rotation track of an object is synchronized. If not, it will be synchronized.
