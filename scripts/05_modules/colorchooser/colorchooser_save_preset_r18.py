"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Loads the swatches of the given BaseDocument and stores them as a preset.

Note:
    - The ColorSwatchData of the active document must contain some colors.

Class/method highlighted:
    - c4d.modules.colorchooser.SwatchData
    - c4d.modules.colorchooser.GetColorSwatchPresetDirectory()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Creates a new ColorSwatchData
    swatchData = c4d.modules.colorchooser.ColorSwatchData()
    if swatchData is None:
        raise MemoryError("Failed to create a ColorSwatchData.")

    # Loads color groups from the active document
    if not swatchData.Load(doc):
        raise RuntimeError("Failed to load the ColorSwatchData.")

    # Builds preset URL
    url = c4d.modules.colorchooser.GetColorSwatchPresetDirectory()
    url = url + "/newColorPreset"

    # Saves color swatches preset
    if not swatchData.SavePresetByURL(url, "User", "This is my preset"):
        raise RuntimeError("Failed to save the color swatch preset.")

    print("Color swatch preset saved successfully")

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
