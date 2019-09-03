# Polygon Reduction

The PolygonReduction class allows reducing the polygon count of a given PolygonObject while retaining its overall shape. The class gives access to the functionalities used within the "Polygon Reduction" generator.

Classic API:
- **c4d.utils.PolygonReduction**: *Reduces the polygon count of a given PolygonObject while retaining its overall shape.*

## Examples

### polygonreduction_create
Version: R19, R20, R21 - Win/Mac

    Creates a new PolygonReduction object.

### polygonreduction_edgelevel
Version: R19, R20, R21 - Win/Mac

    Reduces the active PolygonObject to the given edge count.
    
### polygonreduction_preprocess
Version: R19, R20, R21 - Win/Mac

    Configures the given PolygonReduction object.
    Reduces the given PolygonObject to 25%.

### polygonreduction_trianglelevel
Version: R19, R20, R21 - Win/Mac

    Reduces the active PolygonObject to the given triangle count.

### polygonreduction_vertexlevel
Version: R19, R20, R21 - Win/Mac

    Reduces the active PolygonObject to the given vertex count.
