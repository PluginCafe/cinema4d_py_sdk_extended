# Geometry
Provides examples for geometry types in the Cinema API.

All geometry in the Cinema 4D Cinema API is represented as `BaseObject` instances. `BaseObject` instances can also express non-geometry entities as light objects or cameras, but they are being ignored in this context. There are two fundamental types of geometry representations in the Cinema API:

* Generator objects
* Non-generator objects

Realized are most forms of Cinema API geometry by the following type hierarchy (there are some outliers as for example VolumeObject which have their own type, but these are still all `BaseObject` instances):

    c4d.BaseObject
    +- c4d.PointObject
        +- c4d.LineObject
        +- c4d.PolygonObject
        +- c4d.SplineObject

Generator objects are objects which generate some form of geometry over their parameters exposed in the Attribute Manager of Cinema 4D. Generators objects can generate both polygon and curve geometry. An example would be the Cube generator object which has parameters for its size, segments and fillets. Changing the parameters of the Cube generator object will then regenerate its underlying cache which represents the generator in the viewport and renderings. Generator objects do not allow users to modify their underlying cache manually which also applies to programmatic access.

Non-generator objects on the other hand do not have any parameters which are exposed in the Attribute Manager which would influence their geometry. The two types which follow this model are `LineObject` and `PolygonObject`, both derived from `PointObject` . `PolygonObject` represents discrete polygonal data over vertices and polygons, and `LineObject` represents discrete curve data over points and segments. The outlier from this model is the type `SplineObject` which is representing splines. It is both a `PointObject` and a generator object. Spline generator objects in the sense of parametric objects, as for example the Circle Spline object, return directly spline caches in the form of `LineObject`. But user-editable splines, `SplineObject` instances, also have a `LineObject` cache for their current interpolation settings. 

There are two types of geometry caches in the Cinema API. Caches for internal representations of generator objects, they are plainly referred to as *caches*, and *deform caches*; which can only be found on non-generator objects. The cache of a generator object represents the set of parameters the generator object had when the cache was built. In the case of simple generators, as for example the Cube generator object, the cache is a `PolygonObject`, representing the polygons of that generator. But generator object caches can be much more complex, where the cache of the generator is a hierarchy of objects, including other generator objects with their own caches. 

Deform caches can only be found on non-generator `PointObject` objects and they are generated when a deformer, e.g., the Bend object, is applied to them. These caches then represent the deformed state of the `PolygonObject` or `LineObject` and realize the non-destructive nature of deformers in Cinema 4D. Since many objects in a scene can be generator objects, deform caches are often buried deep within the cache of a generator object.

## Examples

| File | Description |
| :-   | :-          |
| geometry_caches_xxx.py | Explains the geometry model of the Cinema API in Cinema 4D. |
| geometry_polygonobject_xxx.py | Explains the user-editable polygon object model of the Cinema API. |
| geometry_splineobject_xxx.py | Explains the user-editable spline object model of the Cinema API. |
| operation_extrude_polygons_xxx.py | Demonstrates how to extend polygonal geometry at the example of extruding polygons. |
| operation_flatten_polygons_xxx.py | Demonstrates how to deform points of a point object at the example of 'flattening' the selected polygons in a polygon object. |
| operation_transfer_axis_xxx.py | Demonstrates how to 'transfer' the axis of a point object to another object while keeping its vertices in place. |