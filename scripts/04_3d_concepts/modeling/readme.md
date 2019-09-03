# Modeling

The classic Cinema 4D provides the base classes for modeling in Cinema 4D. The MAXON API provides further, advanced modeling tools.

Modeling operations can be performed directly on the edited object or with the c4d.utils.SendModelingCommand() function.

Classic API:
- **c4d.PointObject**: *Base class for objects that contain points.*
- **c4d.SplineObject**: *Represents a Spline object based on PointObject.*
- **c4d.PolygonObject**: *Represents a Polygon object based on PointObject.*
- **c4d.utils.PolygonReduction**: *Reduces the polygon count of a given PolygonObject while retaining its overall shape.*
- **c4d.VertexColorTag**: *A c4d.VariableTag that stores RGBA colors for the polygons of the host polygon object*
- **c4d.UVWTag**: *Stores UVW coordinates for a (polygon) object. For each polygon a set of four UVW coordinates is stored*
- **c4d.NormalTag**: *Stores normal vectors for a (polygon) object. For each polygon a set of four vectors is stored.*

Maxon API:
- **maxon.frameworks.mesh_misc**: *Contains class to Get/Set mesh attributes from a c4d.CustomDataTag.*

## Content

* **polygon_reduction**: *Reduces the polygon count of a given PolygonObject while retaining its overall shape.*

* **vertex_color_tag**: *Adds additional color information to a polygon object*

## Examples

### read_write_normal_tag
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21 - Win/Mac

    Reads and Write the Raw Data of a Normal Tag.
    Normals are stored for each vertex of each polygon.
    Raw Data normal structure for one polygon is 12 int16 value (4 vectors for each vertex of a Cpolygon * 3 components for each vector) even if the Cpolygon is a Triangle.
