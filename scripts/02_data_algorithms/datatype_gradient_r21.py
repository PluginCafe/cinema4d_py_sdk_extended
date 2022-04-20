"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam, Ferdinand Hoppe

Description:
    - Showcases the usage of the custom data type `c4d.Gradient`.
    - Creates a material with a gradient shader in the color channel.

Class/method highlighted:
    - c4d.BaseMaterial
    - c4d.BaseShader
    - c4d.Gradient
    - c4d.BaseContainer

"""

import c4d

def main():
    # Create a new material and a new gradient shader.
    material = c4d.BaseMaterial(c4d.Mmaterial)
    shader = c4d.BaseShader(c4d.Xgradient)
    
    # Get a copy of the c4d.Gradient data referenced by the gradient shader
    # and a copy of the knot data stored in the c4d.Gradient data. The knot
    # data is expressed as a c4d.BaseCoontainer.
    gradient = shader[c4d.SLA_GRADIENT_GRADIENT]
    knotData = gradient.GetData(c4d.GRADIENT_KNOT)
    
    # Iterate over all knots in the knot data container and set their 
    # interpolations to linear. Each knot in the knot data container is itself 
    # a c4d.BaseContainer, storing the data for a single knot.
    for _, knot in knotData:
        knot[c4d.GRADIENTKNOT_INTERPOLATION] = c4d.GRADIENT_INTERPOLATION_NONE

    # Items can also be retrieved by their index from a BaseContainer, here 
    # the first index, i.e., second item, in the container. In this case the 
    # position of the knot is written and then the knot container is being 
    # written back into the index its has been retrieved from.
    knot = knotData.GetIndexData(1)

    knot[c4d.GRADIENTKNOT_POSITION] = 0.5
    knotData.SetIndexData(1, knot)
    
    # After these modifications the knots must be written back into the 
    # c4d.Gradient data, because GetData() returned a copy above. This also
    # does apply to the shader and its gradient for the same reason.
    gradient.SetData(c4d.GRADIENT_KNOT, knotData)
    shader[c4d.SLA_GRADIENT_GRADIENT] = gradient
    
    # Aside from assigning the shader to the correct parameter of the 
    # material, it is also important to call BaseList2D.InsertShader(), as 
    # otherwise the setup will not work.
    material.InsertShader(shader)
    material[c4d.MATERIAL_COLOR_SHADER] = shader

    # Finally, the material is being inserted into the active document and an
    # update event is being pushed event to Cinema 4D, so that its GUI can 
    # catch up to our changes. 'doc' is a predefined module attribute in 
    # script manger scripts which points to the active document. It is
    # equivalent to c4d.documents.GetActiveDocument().
    doc.InsertMaterial(material)
    c4d.EventAdd()

if __name__=='__main__':
    main()