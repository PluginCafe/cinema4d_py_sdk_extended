"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Calculates an RGB value from a light color and applies it to the given "Light" object.

Class/method highlighted:
    - c4d.modules.colorchooser.ColorKelvinTemperatureToRGB()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21
"""
import c4d


def main():
    # Retrieves active object
    if op is None:
        raise RuntimeError("Failed to retrieve the active object.")

    # Checks active object is a light
    if not op.IsInstanceOf(c4d.Olight):
        raise TypeError("The selected object is not a light object.")

    # Initializes Kelvin temperature
    kelvin = 2600.0 # Light bulb

    # Converts Kelvin temperature to RGB color
    rgb = c4d.modules.colorchooser.ColorKelvinTemperatureToRGB(kelvin)

    # Sets the result RGB color as the light object's color
    op[c4d.LIGHT_COLOR] = rgb

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()