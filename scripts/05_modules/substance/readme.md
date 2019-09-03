# Substance Engine

Allegorithmic Substance is a procedural texturing system. Substance assets can be created with Substance Designer from Allegorithmic and imported by Cinema 4D using the described API.

Multiple functions allow to handling Substance assets and shaders.
Substance assets and shaders may also be handled directly.

Classic API:
- **c4d.modules.substance**: *The module providing static methods to use the Substance Engine.*

## Examples

### substance_create_shader
Version: R18, R19, R20, R21 - Win/Mac

    Creates a new substance shader linked to the given substance asset.
    The asset is scanned for a bump output channel that is used in that shader.

### substance_loops_graph_input_output
Version: R18, R19, R20, R21 - Win/Mac

    Loops through the graphs of the given substance asset.
    Loops through the inputs and outputs of each graph.

### substances_create_material
Version: R18, R19, R20, R21 - Win/Mac

    Creates a material from the given substance asset.

