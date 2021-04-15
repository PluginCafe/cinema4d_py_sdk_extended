# Scene Handling

A 3D scene is represented by a BaseDocument. Such a BaseDocument, get several utility functions to configure, organize the projects.
Multiples BaseDocument can be handled at the same time by Cinema 4D.

Classic API:
- **c4d.documents**: *Class storing statics methods for general Cinema 4D documents handling e.g. loads a new document.*
- **c4d.documents.BaseDocument**: *This class contains the complete description of a scene.*
- **c4d.documents.LayerObject**: *Represents a layer in a document.*
- **c4d.documents.RenderData**: *Contains a container with all render settings.*
- **c4d.documents.BaseVideoPost**: *Represents a videopost node.*

## Examples

### basedocument_animate

    Animates a BaseDocument from frame 5 to 20.
    Updates the Progress Bar of Cinema 4D.

### basedocument_creates_marker

    Creates 2 markers.

### basedocument_creates_render

    Creates a new temporary BaseDocument with selected objects.
    Renders it and delete it.

### basedocument_loops_marker

    Iterates over all markers of the active document.
    Prints all markers of the Frame 30.

### basedocument_loops

    Loops over all documents opened in Cinema 4D.

### basedocument_read_animated_mesh

    Animates a BaseDocument from frame 5 to 20.
    Retrieves all the deformed mesh from the selected object.
    Creates a Null for each frame at the position of point 88 of all deformed mesh.
    
### basedocument_undo

    Creates two Undos steps (the user will have to press two times Undo to come back to the initial state of the scene).
    In the first step, a null, a cube, a material, and a texture tag is created. Texture tag is attached to the cube, and the material is assigned to it.
    In the second step, the texture tag is deleted and the cube is moved under the null.

### c4datom_unique_id

    Adds a unique ID to the active Object.
    Iterate all uniques IDs of the active Object.
    Find a particular unique ID from the active object.

### layer_creates

    Creates a New Layer.
    Selects this layer in the Layer Manager.
    Enables the Lock Layer.
    Adds the selected object to this Layer.
    
### multipass_creates

    Creates a new object buffer multipass.
    Inserts it into the currently active render setting.
    
### renderdata_read_engine

    Retrieves the active Render Data (Render Settings).
    Prints the Render Engine ID.
    
