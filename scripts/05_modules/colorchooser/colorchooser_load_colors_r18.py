"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Loads a Cinema 4D scene file to get the stored color swatches.
    - The loaded swatches are applied to the active document.

Class/method highlighted:
    - c4d.modules.colorchooser.SwatchData
    - SwatchData.Load()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21, S22, R23
"""
import c4d
import os


def main():

    # Selects the c4d file to load
    filename = c4d.storage.LoadDialog(type=c4d.FILESELECTTYPE_SCENES, title="Choose File.", flags=c4d.FILESELECT_LOAD, force_suffix="c4d")
    if not filename:
        return

    # Checks selected file is a c4d scene file
    name, suffix = os.path.splitext(filename)
    if suffix != ".c4d":
        raise RuntimeError("Selected file is not a C4D file format.")

    # Loads the document
    flag = c4d.SCENEFILTER_NONE if c4d.GetC4DVersion() > 20000 else c4d.SCENEFILTER_0
    loadedDoc = c4d.documents.LoadDocument(filename, flag)
    if loadedDoc is None:
        raise RuntimeError("Failed to load the document.")

    # Creates a new ColorSwatchData
    swatchData = c4d.modules.colorchooser.ColorSwatchData()
    if swatchData is None:
        raise MemoryError("Failed to create a ColorSwatchData.")

    # Loads swatches from document
    swatchData.Load(loadedDoc)

    # Stores swatches into the active document
    swatchData.Save(doc)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
