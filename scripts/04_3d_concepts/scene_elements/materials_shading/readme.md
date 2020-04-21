# Material shading

Materials define the surface properties of scene objects. They are stored in the BaseDocument. Shaders are used to define these properties dynamically.

Classic API:
- **c4d.BaseMaterial**: *Base class for all materials in Cinema 4D.*
- **c4d.Material**: *Based on BaseMaterial, represents a Cinema 4D standard material.*
- **c4d.BaseShader**: *Base class for all shaders in Cinema 4D.*

## Examples

### material_create_and_set_to_obj
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Creates a new material.
    Sets the material to the first texture tag (it's created if it does not exist) of the active object.

### material_from_texture_tag
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Gets the material linked to the first texture tag of the active object.

### material_reflectance
Version: R18, R19, R20, R21, S22 - Win/Mac

    Creates a standard c4d Material.
    Creates a new GGX layer.
    Defines some reflectance parameters.


### material_set_to_selected_poly
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Apply the selected material to selected polygons on the selected object.

### material_shader_loops_all
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Loops over all materials, shaders of the active document and display their previews in the Picture Viewer.
    
### shader_create_bitmap
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Creates a standard c4d Material.
    Creates a bitmap shader.
    
### shader_read_layer
Version: R17, R18, R19, R20, R21, S22 - Win/Mac

    Loops over all shaders of the active material.
    If it's a LayerShader, loops over all layers and print its name.