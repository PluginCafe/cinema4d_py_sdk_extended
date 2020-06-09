# BodyPaint

BodyPaint is a module that allows drawing bitmap textures on polygon objects. The BodyPaint API allows accessing the edited textures.
Several utility functions are provided.

Classic API:
- **c4d.modules.bodypaint**: *Provide statics methods to handle UV editing from BodyPaint.*
- **c4d.modules.bodypaint.PaintMaterial**: *Represents a paintable material.*
- **c4d.modules.bodypaint.PaintBitmap**: *Base class for all BodyPaint images classes.*
- **c4d.modules.bodypaint.PaintTexture**: *A texture that contains multiple layers.*
- **c4d.modules.bodypaint.PaintLayer**: *Base class for layers within a PaintBitmap. Layers can be PaintLayerBmp, PaintLayerFolder, or PaintLayerMask.*

## Examples


### call_uv_command
Version: R18, R19, R20, R21, S22 - Win/Mac

    Calls BodyPaint 3D UV commands.

### get_uv_seams
Version: S22.114 - Win/Mac

    Copies the UV seams to the edge polygon selection.
