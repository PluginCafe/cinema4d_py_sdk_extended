# Take System

The Take System makes it possible to handle variations of a scene in one BaseDocument.

Classic API:
- **c4d.modules.takesystem.TakeData**: *Stores the Take data of a given BaseDocument and settings of the Take Manager.*
- **c4d.modules.takesystem.BaseTake**: *Represents a Take and stores the overrides.*
- **c4d.modules.takesystem.BaseOverride**: *Stores the settings of a certain object in a certain Take.*
- **c4d.modules.takesystem.BaseOverrideGroup**: *Acts like a virtual null object and can assign different tags to the objects organized in that group.*

## Examples

### takesystem_autotake
Version: R17, R18, R19, R20, R21 - Win/Mac

    Stores edits of the given sphere object in a Take.

### takesystem_cameras
Version: R17, R18, R19, R20, R21 - Win/Mac

    Creates a new Take for each currently selected camera object.

### takesystem_counter_part
Version: R17, R18, R19, R20, R21 - Win/Mac

    Searches for the BaseOverride of the given material and its color parameter.
    If found, the color value is applied to the backup value and transfers the state of this Take to the backup Take.

### takesystem_cube_override
Version: R17, R18, R19, R20, R21 - Win/Mac

    Adds an override to the current Take for the object (that must be a cube) and changes the "Size" parameter.

### takesystem_loop_takes
Version: R17, R18, R19, R20, R21 - Win/Mac

    Loops through all Takes that are direct child Takes of the main Take.

### takesystem_main_take_current
Version: R17, R18, R19, R20, R21 - Win/Mac

    Checks if the current Take is the main Take. If not, the main Take becomes the current Take.

### takesystem_material_override
Version: R17, R18, R19, R20, R21 - Win/Mac

    Creates 10 Takes with different overrides of the material color.

### takesystem_new_take
Version: R17, R18, R19, R20, R21 - Win/Mac

    Creates a new Take and makes it the current one.

### takesystem_override_group_active
Version: R17, R18, R19, R20, R21 - Win/Mac

    Loops through all override groups and checks which groups are currently selected.

### takesystem_override_group_add
Version: R17, R18, R19, R20, R21 - Win/Mac

    Adds the currently selected objects to the BaseOverrideGroup "group".

### takesystem_override_group_materials
Version: R17, R18, R19, R20, R21 - Win/Mac

    Creates a Take with an override group for each selected material.
    Adds the object "object" to the newly created group.

### takesystem_override_group_modes
Version: R17, R18, R19, R20, R21 - Win/Mac

    Adds the currently selected objects to a new group in the current Take.

### takesystem_override_group
Version: R17, R18, R19, R20, R21 - Win/Mac

    Adds a new Take and creates a new override group for all selected objects.
    If a material with the name "Green" exists a texture tag referencing that material is added to the override group.

### takesystem_renderdata
Version: R17, R18, R19, R20, R21 - Win/Mac

    Gets the first Render Setting and loops through all Render Setting objects.
    Create a Take for each Render Setting.
    
### takesystem_sphere_override
Version: R17, R18, R19, R20, R21 - Win/Mac

    Checks if the given Take contains an override for the given sphere object.
    If so, it is checked if the "Radius" parameter is overridden, in this case, the value is increased and the node updated.

### takesystem_take_to_document
Version: R17, R18, R19, R20, R21 - Win/Mac

    Loops through the child Takes of the main Take
    Save the state of each child Take to a document.
    
### takesystem_userdata
Version: R17, R18, R19, R20, R21 - Win/Mac

    Adds a new boolean userdata parameter to the given BaseTake.
