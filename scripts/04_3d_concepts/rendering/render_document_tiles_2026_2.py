"""Demonstrates how to render a document split into tiles which can be composited back together to 
a full image. 

Create a scene, save it, and then run the script. The script will render the document in 2x2 tiles 
and save the tiles and a composite of all tiles into a folder named <DocumentName>_tiles next to 
the document.
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2026 MAXON Computer GmbH"
__date__ = "08/04/2026"
__license__ = "Apache-2.0 License"
__version__ = "2026.2.0"

import itertools
import os
import shutil

import c4d
import mxutils


doc: c4d.documents.BaseDocument  # The currently active document.
op: c4d.BaseObject | None  # The primary selected object in `doc`. Can be `None`.

TILE_COUNT: tuple[int, int] = (2, 2) # Number of tiles in x and y direction.
KERNEL_BORDER: int = 16 # Number of pixels to render additionally around each tile to avoid seams 
                        # when the render engine is not render region aware (and uses some kind of 
                        # filter kernel in rendering, which is usually the case). We have to guess
                        # here as it is obvious from the out side what the maximum kernel size of a
                        # renderer is for a given rendering.

# List of tile coordinates, e. g., (0, 0), (0, 1), (1, 0), (1, 1) for TILE_COUNT = (2, 2).
TILE_INDICES: list[tuple[int, int]] = list(itertools.product(range(TILE_COUNT[0]), 
                                                             range(TILE_COUNT[1])))

def SaveShowBitmap(bitmap: c4d.bitmaps.BaseBitmap, name: str, directory: str) -> None:
    """Saves the given bitmap as a PSD with the given name in the given directory and also
    displays it in the picture viewer.
    """
    c4d.bitmaps.ShowBitmap(bitmap, name)
    filePath: str = os.path.join(directory, f"{name}.psd")
    if bitmap.Save(filePath, c4d.FILTER_PSD) != c4d.IMAGERESULT_OK:
        raise RuntimeError(f"Failed to save {name} to disk.")

@mxutils.SET_STATUS("Rendering document ...", doSpin=True)
def main() -> None:
    """Called by Cinema 4D when the script is being executed.
    """
    if not doc.GetDocumentPath() or not doc.GetDocumentName():
        return c4d.gui.MessageDialog("Please save the document before running the script.")

    c4d.ClearPythonConsole()

    # The folder where we will save results to. Delete the folder when it already exists, so that 
    # we have a clean slate for the output.
    outPath: str = os.path.join(doc.GetDocumentPath(),
                                     f"{os.path.splitext(doc.GetDocumentName())[0]}_tiles")

    if os.path.exists(outPath):
        os.chmod(outPath, 0o755)
        shutil.rmtree(outPath)
    os.makedirs(outPath, exist_ok=True)

    # Draw a copy of the render data container, so that we can modify it without changing the document.
    rData: c4d.documents.RenderData = doc.GetActiveRenderData()
    renderSettings: c4d.BaseContainer = mxutils.CheckType(
        rData.GetDataInstance().GetClone(c4d.COPYFLAGS_NONE))

    # Get the absolute resolution of the render and compute the x and y size of the tiles based on 
    # the tile count. Also setup the final composite bitmap where we will stitch the tiles together.
    xRes: int = int(renderSettings[c4d.RDATA_XRES_VIRTUAL] or renderSettings[c4d.RDATA_XRES])
    yRes: int = int(renderSettings[c4d.RDATA_YRES_VIRTUAL] or renderSettings[c4d.RDATA_YRES])
    tileXSize: int = xRes // TILE_COUNT[0]
    tileYSize: int = yRes // TILE_COUNT[1]
    composite: c4d.bitmaps.BaseBitmap = mxutils.CheckType(
        c4d.bitmaps.AllocateRenderBitmap(renderSettings))

    # Now we iterate over all tiles and render the document for each tile.
    for x, y in TILE_INDICES:

        # Draw a copy of the render settings for the current tile and then compute the coordinates of
        # the tile within the overall image based on the tile size and the tile index.
        tileSettings: c4d.BaseContainer = renderSettings.GetClone(c4d.COPYFLAGS_NONE)
        xMin, yMin = x * tileXSize, y * tileYSize
        xMax, yMax = (x + 1) * tileXSize, (y + 1) * tileYSize

        # Here we now run into a problem when the render engine is not render region aware in its 
        # rendering. Let us we assume we have an image with the pixel P in it as shown below. And 
        # the rendering applies some kind of filter kernel to the image, so that the value of P is 
        # influenced by its neighboring pixels, here shown as the numbers 1 to 8. This could be
        # anything from a simple box filter, over anti-aliasing filters, to more complex filters 
        # such as motion blur or rendering effects.
        #
        #                               ┌─────────────────────┐
        #                               │       1 2 3         │
        #                               │       8 P 4         │
        #                               │       7 6 5         │
        #                               └─────────────────────┘
        #
        # When we now split up an image into two tiles Ta and Tb via RDATA_RENDERREGION, we end up
        # with this:
        #
        #                               ┌──────────┬──────────┐
        #                               │       1 2│3         │
        #                               │       8 P│4         │
        #                               │ Ta    7 6│5      Tb │
        #                               └──────────┴──────────┘
        #
        # I.e., in the original rendering, P would be influenced by the pixels 1 to 8, but when we
        # render the tiles separately, P is only influenced by the pixels 1, 2, 6, 7, and 8 because
        # 3, 4, and 5 are not part of the tile Ta anymore and instead are part of the tile Tb. This 
        # means that the pixel P will have a different value within the tile Ta than it would have 
        # in the original rendering.
        #
        # Some render engines such as Redshift are render region aware and already render such
        # renderings with a pixel border around the tile that matches the maximum kernel size, and
        # then return the correctly cropped tile. But other render engines such as the standard 
        # renderer do not do this. Here we have to add a border ourselves and guess a maximum kernel 
        # size. This is what the KERNEL_BORDER constant is for. After the rendering we then have to 
        # crop the tile bitmaps to the original tile size before we stitch them together.

        # You must adopt this to the render engines you are using and ask the vendors if their engine
        # is render region aware or not. For the builtin render engines in Cinema 4D, only RS does it.
        isKernelAware: bool = tileSettings[c4d.RDATA_RENDERENGINE] == c4d.VPrsrenderer

        xMin_: int = max(0, xMin - KERNEL_BORDER) if not isKernelAware else xMin
        yMin_: int = max(0, yMin - KERNEL_BORDER) if not isKernelAware else yMin
        xMax_: int = min(xRes, xMax + KERNEL_BORDER) if not isKernelAware else xMax
        yMax_: int = min(yRes, yMax + KERNEL_BORDER) if not isKernelAware else yMax

        # Now we set the render region for the current tile. Render regions are expressed in relation
        # to their border. So RDATA_RENDERREGION_BOTTOM expresses for example how many pixels the 
        # bottom border the render region is away from the bottom border of the overall image.
        tileSettings[c4d.RDATA_RENDERREGION] = True
        tileSettings[c4d.RDATA_RENDERREGION_LEFT] = xMin_
        tileSettings[c4d.RDATA_RENDERREGION_TOP] = yMin_
        tileSettings[c4d.RDATA_RENDERREGION_RIGHT] = xRes - xMax_
        tileSettings[c4d.RDATA_RENDERREGION_BOTTOM] = yRes - yMax_

        # Now we render the document for the current tile using our tile settings. The bitmap we
        # render into has to be of the full size of the overall image, because RenderRegion works
        # in Cinema 4D in a way that you get a full size image as a result, but only the pixels in
        # the render region are actually rendered. So, for clarity I used #settings here, but you 
        # could also pass #tileSettings, #AllocateRenderBitmap will ignore render region settings.
        bmp: c4d.bitmaps.MultipassBitmap = mxutils.CheckType(
            c4d.bitmaps.AllocateRenderBitmap(renderSettings))
        flags = c4d.RENDERFLAGS_AUTO_SETUP | c4d.RENDERFLAGS_OCIO_BAKE_RENDERING
        if c4d.documents.RenderDocument(doc, tileSettings, bmp, flags) != c4d.RENDERRESULT_OK:
            raise RuntimeError("Rendering failed.")

        # Now we save out the (cropped back) tile and also copy it to the composite. I am not 
        # handling multi pass layers here which would be an extra layer of complexity, but is
        # absolutely doable. I.e., we just composite the final RGBA result here.

        xMinOut: int = xMin_ if isKernelAware else xMin
        yMinOut: int = yMin_ if isKernelAware else yMin
        xMaxOut: int = xMax_ if isKernelAware else xMax
        yMaxOut: int = yMax_ if isKernelAware else yMax
        if not isKernelAware:
            cropped: c4d.bitmaps.BaseBitmap = bmp.GetClonePart(
                xMinOut, yMinOut, xMaxOut - xMinOut, yMaxOut - yMinOut)
            SaveShowBitmap(cropped, f"Tile ({x}, {y})", outPath)
        else:
            SaveShowBitmap(bmp, f"Tile ({x}, {y})", outPath)

        print(f"Rendered tile ({x}, {y}) with render region ({xMin_}, {yMin_}, {xMax_}, {yMax_})"
              f" and output region ({xMinOut}, {yMinOut}, {xMaxOut}, {yMaxOut}), ")

        # We are going to copy data row by row into the composite. #bytesPerPixel is the number of
        # bytes each pixel occupies in the bitmap. #tileWidth is the width in pixels of the tile we 
        # are copying, and #buffer is the line buffer we use for copying. We then copy from the min
        # x coordinate up to the width of the tile (i.e., max x coordinate) for each y-coordinate of 
        # the tile. It is important to use the color mode of the tile, and not the color mode of the
        # composite for both the getting and setting of pixels.
        bytesPerPixel: int = bmp.GetBt() // 8
        tileWidth: int = xMaxOut - xMinOut
        buffer: bytearray = bytearray(tileWidth * bytesPerPixel)
        for y_ in range(yMinOut, yMaxOut):
            bmp.GetPixelCnt(xMinOut, y_, tileWidth, buffer, bytesPerPixel, bmp.GetColorMode(), 
                            c4d.PIXELCNT_NONE)
            composite.SetPixelCnt(xMinOut, y_, tileWidth, buffer, bytesPerPixel, bmp.GetColorMode(), 
                                  c4d.PIXELCNT_NONE)

    # Finally, we copy over the color profiles from the last rendered tile to the composite. We have to
    # do this because the renderer will set the final color profiles of an image, #AllocateRenderBitmap
    # will only return an image with the default profiles as it cannot know them in advance.
    for space in (c4d.COLORPROFILE_INDEX_IMAGE, c4d.COLORPROFILE_INDEX_RENDERSPACE, 
                  c4d.COLORPROFILE_INDEX_VIEW_TRANSFORM, c4d.COLORPROFILE_INDEX_DISPLAYSPACE):
        composite.SetColorProfile(bmp.GetColorProfile(space), space)
    
    SaveShowBitmap(composite, "Composite Result", outPath)
    print(f"Saved {len(TILE_INDICES)} rendered tiles and compositing to: {outPath}")


if __name__ == '__main__':
    main()