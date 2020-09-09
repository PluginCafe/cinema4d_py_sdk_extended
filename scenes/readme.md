# Scenes

This folder contains scenes which embed Python usage from different contexts.

## Python Effector
The Python Effector is used to create custom Effector for a MoGraph object. It can be found in the MoGraph -> Effector menu.
See [Python Effector Manual](https://developers.maxon.net/docs/Cinema4DPythonSDK/html/manuals/introduction/python_effector.html)

 ### py_effector_push_apart
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac
    
    Applies a push apart effect on all clones so they don't intersect each other.

 ### py_effector_random
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac
    
    Distributes clones in random position.
    
 ### py_effector_shape
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac
    
    Distributes clones to form different shape (torus, knot, etc..).

## Python Field Object / Layer
A Python Field Object and a Python Field Layer are two differents components of the Field system (replacement of Fallof).
The main purpose is to sample inputs points and assign a weight value to define how much an effector should affect them. 
See [Python Field Object / Layer Manual](https://developers.maxon.net/docs/Cinema4DPythonSDK/html/manuals/introduction/python_field.html)
 
### py_field_object_color_direction
Version: R20, R21, S22, R23 - Win/Mac

    A Python Field Object, setting colors and positions in multiple effectors.
    
### py_field_modifier_readcolor
Version: R20, R21, S22, R23 - Win/Mac

    A Python Field Layer, setting positions according to previous fields colors.

### py_field_modifier_vertexmap
Version: R20, R21, S22, R23 - Win/Mac
    
    A Python Field Layer in a vertex map, sampling a Random Field Object sets to noise.

## Python Generator
A Python Generator is used to generate an object(s) in Python. It can be found in the generator menu.
See [Python Generator Manual](https://developers.maxon.net/docs/Cinema4DPythonSDK/html/manuals/introduction/python_generator.html)

### py_generator_binary_kite
Version: R20, R21, S22, R23 - Win/Mac

    A basic Python Generator.
    
### py_generator_mengersponge
Version: R20, R21, S22, R23 - Win/Mac

    Outputs a cube in a Menger Sponge distribution.

## Python Tag
A Python Tag is used to write and execute Python code. It can be found in the scripting part of the Tag Menu.
See [Python Scripting Tag Manual](https://developers.maxon.net/docs/Cinema4DPythonSDK/html/manuals/introduction/python_tag.html)

### py_tag_boid_simulation
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Generates and updates Thinking Particle.

### py_tag_cs_buildon
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Changes object positions, and scale over time to assemble a car.
    
### py_tag_cube_sin
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Changes object position according to the current frame following a sin wave.

### py_tag_light_intensity
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Links the intensity of light with the current frame.
    
### py_tag_sa4_python
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Modifies Thinking Particle position following Strange Attractor algorithm.
