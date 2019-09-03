# Vertex Color Tag

Color attributes can be assigned to vertex through a Vertex Color Tag that stores RGBA colors for the polygons of the host polygon object
The tag can be either in point mode or polygon mode. In point mode it will store color information for each vertex of the object.
In polygon mode it will store color information for each vertex of each polygon of the object.

Classic API:
- **c4d.VertexColorTag**: *A c4d.VariableTag that stores RGBA colors for the polygons of the host polygon object*

## Examples

### vertex_color_tag_point_mode
Version: R18, R19, R20, R21 - Win/Mac

    Gets and Sets Vertex Colors in Point mode:
    Changes all black Vertex Colors to red.

### vertex_color_tag_polygon_mode
Version: R18, R19, R20, R21 - Win/Mac

    Gets and Sets Vertex Colors in Polygon mode:
    Changes all vertex colors to red.
