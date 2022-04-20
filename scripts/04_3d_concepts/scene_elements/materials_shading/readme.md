# Material shading

Materials define the surface properties of scene objects. They are stored in the BaseDocument. Shaders are used to define these properties dynamically.

Classic API:
- **c4d.BaseMaterial**: *Base class for all materials in Cinema 4D.*
- **c4d.Material**: *Based on BaseMaterial, represents a Cinema 4D standard material.*
- **c4d.BaseShader**: *Base class for all shaders in Cinema 4D.*

## Examples

### material_create_and_set_to_obj

    Creates a new material.
    Sets the material to the first texture tag (it's created if it does not exist) of the active object.

### material_from_texture_tag

    Gets the material linked to the first texture tag of the active object.

### material_reflectance

    Creates a standard c4d Material.
    Creates a new GGX layer.
    Defines some reflectance parameters.

### material_set_to_selected_poly

    Apply the selected material to selected polygons on the selected object.

### material_shader_loops_all

    Loops over all materials, shaders of the active document and display their previews in the Picture Viewer.
    
### shader_create_bitmap

    Creates a standard c4d Material.
    Creates a bitmap shader.
    
### shader_read_layer

    Loops over all shaders of the active material.
    If it's a LayerShader, loops over all layers and print its name.

### shader_variation

    Creates a material and add a variation shader, adds some layers and updates parameters
    The variation shader allow to add some layers and defines the texture links with python and c++
    To "simulate" the button pressed, we need to define the right parameter with a value of 0. This will trigger the event
    that will execute the function corresponding to the button pressed.