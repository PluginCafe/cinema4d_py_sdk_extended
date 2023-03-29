# Modelling
Both the classic API and the maxon API provide types of geometry representations and modelling tools for them. The maxon API represents geometry with Scene Nodes, which are currently not yet documented in Python. Documented are here the classic API geometry representations and the modelling tools which exist for them, both in the classic and maxon API.

## geometry
Provides examples for the fundamental geometry types `PointObject`, `SplineObject`, `PolygonObject`, `LineObject`, and `Cpolygon`, how to construct and manipulate them, as well as for the concept of caches used by them. The manipulation and construction examples provided here are of more fundamental nature. For using existing modelling tools, see the section *modelling_commands*.

## modelling_commands
Provides examples for executing builtin modelling tools as the *Extrude* or *Current State to Object* tool with the function `SendModelingCommand`.

## polygon_reduction
Provides examples for reducing the polygon count of `PolygonObject` instances while retaining their shape with the `PolygonReduction` type.

## uvw_tag
Provides examples for the type `VertexColorTag` which storing per vertex color information for `PolygonObject` instances.

## vertex_color_tag
Provides examples for the type `VertexColorTag`, a tag storing per vertex color information for a `PolygonObject` instance which can be used in shaders.

## read_write_normal_tag.py
Provides an example for reading normal data from and writing normal data to the type `NormalTag`.



