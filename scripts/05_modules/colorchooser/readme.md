# Color Chooser

The color Chooser libraries provide Color swatches and color utility functions.
Color swatches are a system to handle colors or color groups. These color groups can be stored with Cinema 4D itself, a BaseDocument or a preset.

Classic API:
- **c4d.modules.colorchooser**: *Provides statics methods to handle color.*
- **c4d.modules.colorchooser.ColorSwatchData**: *Stores multiple ColorSwatchGroup objects.*
- **c4d.modules.colorchooser.ColorSwatchGroup**: *Stores multiple colors as maxon::ColorA.*

## Examples


### colorchooser_color_to_string
Version: R18, R19, R20, R21, S22, R23 - Win/Mac

    Reads the color parameter of the given material and prints the value as RGB and HSV.

### colorchooser_complementary
Version: R18, R19, R20, R21, S22, R23 - Win/Mac

    Reads the color value from the active material.
    Calculates the complementary color and applies it to new material.

### colorchooser_kelvin_to_rgb
Version: R18, R19, R20, R21, S22, R23 - Win/Mac

    Calculates an RGB value from a light color and applies it to the given "Light" object.

### colorchooser_load_colors
Version: R18, R19, R20, R21, S22, R23 - Win/Mac

    Loads a Cinema 4D scene file to get the stored color swatches.
    The loaded swatches are applied to the active document.

### colorchooser_new_group
Version: R18, R19 - Win/Mac
See colorswatch_create_new_group_and_color_r20 for an updated R20 version.

    Adds a new color group to the active document.

### colorchooser_save_preset
Version: R19, R20, R21, S22, R23 - Win/Mac

    Loads the swatches of the given BaseDocument and stores them as a preset.
    
### colorswatch_create_new_group_and_color
Version: R20, R21, S22, R23 - Win/Mac

    Creates a swatch group and adds rainbow colors to it.
        
### colorswatch_creatematerials
Version: R19, R20, R21, S22, R23 - Win/Mac

    Reads all the colors from the first swatch group in the active document and creates material for each one.
