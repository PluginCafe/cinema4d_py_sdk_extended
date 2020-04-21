"""
Copyright: MAXON Computer GmbH
Author: Andreas Block

Description:
    - Creates a material from the given substance asset.

Class/method highlighted:
    - c4d.modules.substance.GetFirstSubstance()
    - c4d.modules.substance.PrefsGetMaterialModeSetting()
    - c4d.modules.substance.CreateMaterial()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21, S22
"""
import c4d


def main():
    # Retrieves first substance
    substance = c4d.modules.substance.GetFirstSubstance(doc)
    if substance is None:
        raise RuntimeError("Failed to retrieve the first substance (most likely there is no substance).")

    # Retrieves material creation mode set in Substance preferences
    mode = c4d.modules.substance.PrefsGetMaterialModeSetting()
    if mode is None:
        raise RuntimeError("Failed to retrieve the material mode setting.")

    # Creates material based on the passed Substance asset
    mat = c4d.modules.substance.CreateMaterial(substance, 0, mode)
    if mat is None:
        raise MemoryError("Failed to create a substance material.")

    # Changes name and insert material into the document
    mat.SetName(substance.GetName() + " Material From Script")
    doc.InsertMaterial(mat)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
        main()
