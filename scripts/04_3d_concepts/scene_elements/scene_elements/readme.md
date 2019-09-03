# Scene Elements

A 3D scene is composed of objects of different types like polygon meshes, lights, and cameras. Additionally, the scene graph of Cinema 4D can contain generators and deformers.

Classic API Object:
- **c4d.BaseObject**: *Base class for all objects, generators, deformers, etc.*
- **c4d.CameraObject**: *Represents a scene camera.*
- **c4d.InstanceObject**: *References another scene object.*

Classic API Tag:
- **c4d.BaseTag**: *Base class for all tags.*
- **c4d.VariableTag**: *Base class for tags storing multiple data elements with variable size.*
- **c4d.TextureTag**: *A TextureTag is used to assign a material (BaseMaterial) to a BaseObject.*
- **c4d.UVWTag**: *Stores UVW coordinates for a (polygon) object.*
- **c4d.NormalTag**: *Stores normal vectors for a (polygon) object.*

## Examples

### instanceobject_create
Version: R20, R21 - Win/Mac

    Instantiates 100 cubes, with an InstanceObject.
    Offsets each instance with a custom Matrix.
    Colorizes each instance with a custom color.

### instanceobject_matrix
Version: R20, R21 - Win/Mac

    Distributes and creates Sphere along a Matrix Object with an InstanceObject.

