# Rendering

The classic API provides tools to render a given BaseDocument.

Classic API:
- **c4d.documents.RenderData**: *Represents a set of render settings of a BaseDocument.*
- **c4d.modules.render.InitRenderStruct**: *Prepares a material or a shader for sampling.*

## Examples

### render_current_frame
Version: R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Adjusts the active Render Settings to render the current frame based on user settings.

### render_ogl_half_size
Version: R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Adjusts the active Render Settings to produce a halfsize OGL render.
    Resets back to your original settings when render is launched.

### render_settings_double_size
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Double the size of the render from the active Render Settings.

### render_settings_openexr_data
Version: R20, R21, S22 - Win/Mac

    Configures OpenEXR output render format with SetImageSettingsDictionary() then reads these with GetImageSettingsDictionary().
    
### render_with_progress_hook
Version: R21, S22 - Win/Mac

    Render the current document with a progress hook to get notified about the current rendering progress.
