# Polygon Reduction

The PolygonReduction class allows reducing the polygon count of a given PolygonObject while retaining its overall shape. The class gives access to the functionalities used within the "Polygon Reduction" generator.

Classic API:
- **c4d.utils.PolygonReduction**: *Reduces the polygon count of a given PolygonObject while retaining its overall shape.*

## Examples

### polygonreduction_create

    Creates a new PolygonReduction object.

### polygonreduction_edgelevel

    Reduces the active PolygonObject to the given edge count.
    
### polygonreduction_preprocess

    Configures the given PolygonReduction object.
    Reduces the given PolygonObject to 25%.

### polygonreduction_trianglelevel

    Reduces the active PolygonObject to the given triangle count.

### polygonreduction_vertexlevel

    Reduces the active PolygonObject to the given vertex count.
