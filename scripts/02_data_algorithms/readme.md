# Data & Algorithms

Both the classic API and the MAXON API provide simple and complex data types, data structures and basic algorithms.

It is advised to always use these data types instead of basic data types or standard library structures. Using the provided data types ensures compatibility with all supported platforms.

Classic API:
- **c4d.BaseContainer**: *A collection of individual values. Each value has its own ID and type.*
- **c4d.Vector**: *A structure composed of three floating-point values. Such a vector is typically used to represent a position in 3D space, a direction, normals, a rotation or a color value.*
- **c4d.Matrix**: *Represents the transformation from one coordinate system to another. The typical use case is the transformation matrix that defines the position, rotation and scale of an object in 3D space.*
- **c4d.BaseTime**: *Represents a point in time in a BaseDocument. BaseTime internally stores the time values as exact fractions independent of the frame rate*
- **c4d.utils.noise.C4DNoise**: *Class used for the Cinema 4D shaders.*

Maxon API:
- **maxon.Data**: *A generic container that can store any MAXON API data type.*
- **maxon.BaseArray**: *A generic array class template used to stored any kind of maxon.Data.*
- **maxon.Tuple**: *A static storage for maxon.Data types. It is similar to a pair, but supports a variable number of elements.*
- **maxon.DataDictionary**: *A data container that stores arbitrary MAXON API data filed under a given key*

## Examples

### basecontainer_basic
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Basic usage of a BaseContainer.

### basecontainer_iterates
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Iterates over the content of a BaseContainer.

### c4dnoise_luka
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Creates a Luka Noise into a BaseBitmap.
    Displays this BaseBitmap into the Picture Viewer.

### icondata_basic
Version: R21, S22 - Win/Mac 

    Displays the icon of the selected object into the Picture Viewer.
    Before R21 it's possible to call BaseList2D.GetIcon which will returns a dictionary representing an IconData.

### maxon_basearray
Version: R20, R21, S22 - Win/Mac

    Creates a BaseArray of maxon.Int (any maxon type is working).

### maxon_datadictionary
Version: R20, R21, S22 - Win/Mac

    Converts a Python dictionary to a Maxon Data Dictionary.
 
### maxon_tuple
Version: R20, R21, S22 - Win/Mac

    Creates a Maxon Tuple of 3 fields (any maxon type is working).
    