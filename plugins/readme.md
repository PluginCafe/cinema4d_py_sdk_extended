# Plugins

This folder contains plugins that should be copied in the plugins folder of Cinema 4D:

- Windows: C:/Users/{username}/AppData/Roaming/MAXON/{cinemaversion}/plugins
- macOS: /Users/{username}/Library/Preferences/MAXON/{cinemaversion}/plugins

## CommandData
A data class for creating command plugins. (Previously known as menu plugins.)

### py-cv_rss
Version: R23 - Win/Mac

    Creates a Dialog which display the latest RSS feed of Cineversity.
    Opens the web browser of the current displayed news when the user click a button.
    
### py-memory_viewer
Version: R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Creates a Dialog which display the memory usage.
    The Memory Usage is displayed in a custom Gadget (GeUserArea).

### py-texture_baker
Version: R18, R19, R20, R21, S22, R23 - Win/Mac

    Creates a Dialog to manage texture baking.
    Bakes selected object diffuse to the uv and display the result in the Picture Viewer.
    
### py-sculpt_save_mask
Version: R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Command, rasterizing(baking) the mask data to a bitmap using the first found UV tag on the sculpt object.
    Illustrates the ability to access the mask data on a sculpt object.
    
## ObjectData
A data class for creating object plugins.
An object plugin can either be a generator, a modifier, a spline generator or a particle modifier. 
This is set when the object is registered and affects which functions are called.

### py-dynamic_parameters_object
Version: R18, R19, R20, R21, S22, R23 - Win/Mac

    Generator, which handle dynamics descriptions and link the parameter angle of first phong tag from the generator.
    
### py-custom_icon
Version: R21, S22, R23 - Win/Mac

    Demonstrates how to define a custom icon color according to the new Cinema 4D R21 icon features.
    
### py-rounded_tube
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Generator, generating a c4d.PolygonObject from nothing (like the Cube).
    Manages handles to drive parameters (works only in R18+).

### py-double_circle
Version: R19, R20, R21, S22, R23 - Win/Mac

    Generator, generating a c4d.SplineObject from nothing (like the spline circle).
    Consists of two circles in a given plane.
    Manages handles to drive parameters.
    Registers Help Callback to display user help, if the user click on show help of a parameter.

### py-offset_y_spline
Version: R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Generator, generating a c4d.SplineObject from a child spline object (like the spline mask generator).
    Retrieves the first child object and offset all its points on the y-axis by a specific value. Tangents are unaffected.
    Demonstrates a Spline Generator that requires Input Spline and Outputs a valid Spline everywhere in Cinema 4D.

### py-spherify_modifier
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Modifier, modifying a point object (like the bend deformer).
    Supports Falloff (R18 and R19 only).

### py-sculpt_modifier_deformer
Version: R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Modifier, modifying a point object using the pull sculpting brush tool.

### py-gravitation
Version: R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Particle Modifier, applying a simple gravitation effect for each particles.
    
## TagData
A data class for creating tag plugins.
Tag plugins appear in the Tag menu of the Object Manager and can be attached to objects.

### py-look_at_camera
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac
        
    Tag, force the host object to look at the camera (like the Look At Camera Tag).
    
## ShaderData

A data class for creating shader (channel shader) plugins.
Shader plugins appear in the popup menu of the channels in the Material Manager

### py-fresnel
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Shader, computing a fresnel effect.

## FalloffData
A data class for creating falloff plugins.
Falloffs appear in any falloff description (unless the flag PLUGINFLAG_HIDE is set during registration) and extend the functionality of effectors and anything that uses falloffs.
Falloff are deprecated in R20 and replaced by Fields, but Falloff keep working for compatibility reason.

### py-noise_falloff
Version: R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac
    
    Falloff, modify how effector sampling occurs in this case using a noise (like the spherical falloff).
    Falloff are deprecated in R20 and replaced by Fields, but Falloff keep working for compatibility reason.
    Manages handles to drive parameters.
    
## ToolData
A data class for creating tool plugins.

### py-liquid_painter
Version: R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Creates a liquid Painter Tool.
    Consists of Metaball and Sphere.
    
### py-tooldata_ui
Version: R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Creates a ToolData with a linkBox on it where it's possible to drag and drop an object.
    When this linked object is clicked, its cloned and added to the document in a random position.

## SculptBrushToolData
A data class for creating brush plugins (not only limited to sculpting).

### py-sculpt_grab_brush
Version: R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Brush Tool, modifying a BaseObject by grabbing all points under the brush.
    
### py-sculpt_pull_brush
Version: R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Brush Tool, modifying a BaseObject by pulling all points under the brush.
    
### py-sculpt_twist_brush
Version: R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Brush Tool, modifying a BaseObject by twisting all points under the brush.
    
### py-sculpt_paint_brush
Version: R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Brush Tool, rasterize the stencil onto the polygons touched by the brush. You will need an active stencil for the brush to work.
    Illustrates the ability to access the stencil for a brush and also how to access the bodypaint layer to apply paint.

## SceneSaverData
A data class for creating scene saver plugins (custom scene file format exporter).

### py-ies_meta
Version: R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Exporter, exporting all IES Meta information from the current document to a txt files.
    Iterates all objects present in the cache of each objects in the scene to retrieve IES light.
    
## BitmapLoaderData
A data class for creating bitmap loader plugins (custom bitmap file format importer).

### py-xample_loader
Version: R23 - Win/Mac

    Creates a Bitmap Loader to import a custom picture format into Cinema 4D.
    
## BitmapSaverData
A data class for creating bitmap saver plugins (custom bitmap file format exporter).

### py-xample_saver
Version: R23 - Win/Mac

    Creates a Bitmap Saver to export a custom picture format into Cinema 4D.
    
## PreferenceData
A data class for defining a new preference category in the Cinema 4D preference dialog.

### py-preference
Version: R19, R20, R21, S22, R23 - Win/Mac

    Exposes parameters as global Preference (EDIT->Preference windows).
    Takes care to store data in the world container, so every part of Cinema 4D can access them.

## Token
A token is a string that will be replaced during the token evaluation time by a string representation.

### py-render_token
Version: R21, S22, R23 - Win/Mac

    Registers two Tokens plugin. One visible in the render setting the other one not.
    A token is a string that will be replaced during the token evaluation time by a string representation.
    
## Licensing
In Cinema R21, the licensing changed but keep in mind python is a scripted language, meaning there is no 100% way to secure it.
At a given time the script will be in the memory.

Please don't implement security/serial checking logic into your plugin, instead, it's preferred to send
the data into a server which will check for the validity of the entered serial.

But due to the nature of python, it will still be more or less easy to bypass any kind of security
and directly register the plugin by editing a plugin source code.

Even if you encrypt your python plugin it will be just harder for the attackers but not impossible.

### py-licensing_example
Version: R21, S22, R23 - Win/Mac

    Demonstrates how a plugin can implements a custom licensing in Python.
    Opens a dialog which asks for the serial of the user, according to the current user_id logged in.
    Saves a fie in the temp folder if the serial is correct so the next startup doesn't ask the serial again.