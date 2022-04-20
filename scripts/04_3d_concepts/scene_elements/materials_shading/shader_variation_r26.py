"""
Copyright: MAXON Computer GmbH
Author: Manuel MAGALHAES
Description:
    - Creates a material and add a variation shader, adds some layers and updates parameters
    - The variation shader now allow to add some layers and defines the texture links with python and c++
    - To "simulate" the button pressed, we need to define the right parameter with a value of 0. This will trigger the event
      that will execute the function corresponding to the button pressed.
"""


from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    
    # Create a variation shader
    variationShader = c4d.BaseList2D(c4d.Xvariation)
    if variationShader is None:
        raise RuntimeError("Failed to create a variation shader.")
    
    # Add another layer in variation shader, to "simulate" the button pressed, we just need to set the parameter to 0.
    # This will create an event that will trigger the function to add a layer.
    # we could also use variationShader.SetParameter(c4d.VARIATIONSHADER_ADD, 0, c4d.DESCFLAGS_SET_NONE)
    variationShader[c4d.VARIATIONSHADER_ADD] = 0

    # Create two color shader
    color1 = c4d.BaseList2D(c4d.Xcolor)
    if color1 is None:
        raise RuntimeError("Failed to create a color shader.")

    color2 = c4d.BaseList2D(c4d.Xcolor)
    if color2 is None:
        raise RuntimeError("Failed to create a color shader.")
    
    # Define a new color for both shaders
    color1[c4d.COLORSHADER_COLOR] = c4d.Vector(1, 0, 0)
    color2[c4d.COLORSHADER_COLOR] = c4d.Vector(0, 1, 0)
    
    # Insert the color shader in the variation shader
    variationShader.InsertShader(color1)
    variationShader.InsertShader(color2)   
        
    # Assign the color shader to the variation layers. We must use the symbol VARIATIONSHADER_LAYER_LINK + layerIndex to target the right layer.(0 is on top)
    variationShader[c4d.VARIATIONSHADER_LAYER_LINK + 0] =  color1
    variationShader[c4d.VARIATIONSHADER_LAYER_LINK + 1] =  color2
    
    # Set the first layer probability to 50% and the second to 70%. We must target the right layer using VARIATIONSHADER_LAYER_PROBABILITY + layerIndex
    variationShader[c4d.VARIATIONSHADER_LAYER_PROBABILITY + 0] = 0.5
    variationShader[c4d.VARIATIONSHADER_LAYER_PROBABILITY + 1] = 0.7
    
    # Normalize the value accross all the layers. (the result snould be 41.6666% for the first layer and 58.33333% for the second)
    # To "simulate" the button pressed, we just need to set that parameter to 0 to trigger the event.
    variationShader [c4d.VARIATIONSHADER_NORMALIZE] = 0
    
    # Print the active state of the first layer
    print ("Layer acrtive is ", variationShader[c4d.VARIATIONSHADER_LAYER_ACTIVE + 1] == True) 
    
    # Deactivate layer one and print again
    variationShader[c4d.VARIATIONSHADER_LAYER_ACTIVE + 1] = False
    print ("Layer acrtive is ", variationShader[c4d.VARIATIONSHADER_LAYER_ACTIVE + 1] == True) 
    
    # Create a standard material and assign the variation shader to the color channel.
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    if mat is None:
        raise RuntimeError("Failed to create a material.")
    mat[c4d.MATERIAL_COLOR_SHADER] = variationShader
    
    # Don't forget to isert the shader in the material.
    mat.InsertShader(variationShader)

    # Insert the material in the document.
    doc.InsertMaterial(mat)
    
    # Push an update event to Cinema 4D
    c4d.EventAdd()

if __name__ == '__main__':
    main()