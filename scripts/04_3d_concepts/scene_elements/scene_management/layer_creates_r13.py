"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a New Layer.
    - Selects this layer in the Layer Manager.
    - Enables the Lock Layer.
    - Adds the selected object to this Layer.

Class/method highlighted:
    - c4d.documents.LayerObject
    - BaseDocument.GetLayerObjectRoot()
    - BaseList2D.InsertUnder()
    - BaseList2D.SetLayerData()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21
"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Retrieves the Root of all Layers
    rootLayers = doc.GetLayerObjectRoot()
    if rootLayers is None:
        raise RuntimeError("Failed to retrieve the Root Layer.")

    # Creates a new Layer in memory
    layer = c4d.documents.LayerObject()
    if layer is None:
        raise RuntimeError("Failed to create a Layer.")

    # Defines the Layer Name
    layer.SetName("My super layer")

    # Inserts the layer into the LayerRoot, in the document
    layer.InsertUnder(rootLayers)

    # Enables the Lock mock of the Layer
    # Possibles Options: "solo": bool, "view": bool, "render": bool, "manager": bool, "locked": bool,
    #                    "generators": bool, "expressions": bool, "animation": bool, "color:" c4d.Vector
    layer.SetLayerData(doc, {"locked": True})

    # Selects the new Layer in the Layer Manager
    layer.SetBit(c4d.BIT_ACTIVE)

    # Adds the selected object to this Layer
    op[c4d.ID_LAYER_LINK] = layer

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()