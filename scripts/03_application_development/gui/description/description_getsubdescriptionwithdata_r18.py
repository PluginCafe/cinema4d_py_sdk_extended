"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Retrieves SubDescription parameters information.

Class/method highlighted:
    - Description.GetSubDescriptionWithData()

"""
import c4d


def main():
    # Retrieves active material
    mat = doc.GetActiveMaterial()
    if mat is None:
        raise RuntimeError("Failed to retrieve the active material.")

    # Obtains a gradient shader
    gradient = mat[c4d.MATERIAL_COLOR_SHADER]
    if gradient is None:
        raise RuntimeError("There is no gradient in the color slot of the material.")

    if gradient.GetType() != c4d.Xgradient:
        raise RuntimeError("The shader in the color slot of the material is not a gradient.")

    # Creates a new Description
    desc = c4d.Description()
    if desc is None:
        raise RuntimeError("Failed to create the description.")

    # Builds the gradient DescID
    descId = c4d.DescID(c4d.DescLevel(c4d.SLA_GRADIENT_GRADIENT, c4d.CUSTOMDATATYPE_GRADIENT, c4d.Xgradient))

    # Retrieves the gradient knots description
    desc.GetSubDescriptionWithData(descId, [gradient], c4d.BaseContainer(), None)

    # Retrieves the gradient data with its knots
    gradientData = gradient[descId]

    # Prints the gradient knots
    knotCount = gradientData.GetKnotCount()
    for idx in range(knotCount):
        print(gradientData.GetKnot(idx))

    # Prints the gradient description
    for bc, paramId, groupId in desc:
        print(bc[c4d.DESC_NAME], paramId[-1].dtype)


if __name__ == '__main__':
    main()
