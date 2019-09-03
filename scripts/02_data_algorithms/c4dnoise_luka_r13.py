"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a Luka Noise into a BaseBitmap.
    - Displays this BaseBitmap into the Picture Viewer.

Class/method highlighted:
    - c4d.bitmaps.BaseBitmap
    - c4d.utils.noise.C4DNoise
    - C4DNoise.Noise()
    - c4d.utils.RangeMap()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21
"""
import c4d


def main():
    # Defines the Size of the Bitmap where the noise will be drawn
    width = 300
    height = 300

    # Creates a bitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise RuntimeError("Failed to create a bitmap.")

    # Initialize the previously created bitmap
    if bmp.Init(width, height, 24) != c4d.IMAGERESULT_OK:
        raise RuntimeError("Failed to initialize the bitmaps.")

    # Creates a C4DNoise
    noise = c4d.utils.noise.C4DNoise(seed=42)
    if noise is None:
        raise RuntimeError("Failed to create a noise.")

    # Initialize FBM computation from the previously created noise
    if not noise.InitFbm(21, 2.1, 0.5):
        raise RuntimeError("Failed to initialize the noise.")

    # Iterates through the bitmap and set the noise value per pixel
    for x in xrange(width):
        for y in xrange(height):

            # Calculates the X and Y position
            posSampled = c4d.Vector(x/float(width), y/float(height), 0)

            # Calculates the noise value based on the position
            noiseResult = noise.Noise(c4d.NOISE_LUKA, False, posSampled * 7.0, octaves=5)

            # Remaps the value from 0-1 to 0-255
            noiseValue = int(c4d.utils.RangeMap(noiseResult, 0.0, 1.0, 0.0, 255.0, clampval=True, curve=None))

            # Defines the pixel color to the noise value
            bmp.SetPixel(x, y, noiseValue, noiseValue, noiseValue)

    # Displays the computed bitmap
    c4d.bitmaps.ShowBitmap(bmp)


if __name__ == "__main__":
    main()