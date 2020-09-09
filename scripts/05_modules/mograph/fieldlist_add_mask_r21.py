"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a FieldList with a formula layer, a mask and another formula layer used as a mask of the first formula layer.
    - Assigns this FieldList to the active object that have a c4d.FIELDS parameter e.g. all MoGraph effectors.

Class/method highlighted:
    - c4d.FieldList
    - c4d.modules.mograph.FieldLayer
    - FieldList.InsertLayer()
    - FieldLayer.AddMask()
    - FieldLayer.GetMaskHead()
    - GeListNode.InsertUnder()

Compatible:
    - Win / Mac
    - R21, S22, R23
"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    if op[c4d.FIELDS] is None or not isinstance(op[c4d.FIELDS], c4d.FieldList):
        raise ValueError("op does not have a field falloff parameter.")

    # Creates a FieldList into the memory
    fieldList = c4d.FieldList()
    if fieldList is None:
        raise MemoryError("Failed to create a FieldList.")

    # Creates a field layer formula
    formulaLayer = c4d.modules.mograph.FieldLayer(c4d.FLformula)
    if formulaLayer is None:
        raise MemoryError("Failed to create a Field Layer Formula.")

    # Inserts the field layer formula into the FieldList
    fieldList.InsertLayer(formulaLayer)

    # Creates a mask for the formula field
    if not formulaLayer.AddMask():
        raise RuntimeError("Failed to create a mask")

    # Creates a field layer formula to be used as mask
    formulaMaskLayer = c4d.modules.mograph.FieldLayer(c4d.FLformula)
    if formulaMaskLayer is None:
        raise MemoryError("Failed to create a Field Layer Formula.")

    # Defines the string of the formula layer that will be used as mask
    formulaMaskLayer[c4d.FORMULAFIELD_STRING] = "u * id / count"

    # Retrieves the GeListHead (root) of the the mask for the formulaLayer
    rootMaskFormulaLayer = formulaLayer.GetMaskHead()
    if rootMaskFormulaLayer is None:
        raise RuntimeError("There is no mask for the passed Field Layer.")

    # Inserts the formula layer under the mask head so it will operate as a mask.
    formulaMaskLayer.InsertUnder(rootMaskFormulaLayer)

    # Defines the FieldList used by the object to the one we generated
    op[c4d.FIELDS] = fieldList

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
