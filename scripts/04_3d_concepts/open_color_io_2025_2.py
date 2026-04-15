"""Demonstrates how to read, write, and convert colors in an OpenColorIO (OCIO) color-managed
document in Cinema 4D.

This script demonstrates how to work with OCIO color data in a scene on a more simple and 
scripting focused level. For concrete advice on how to deal with OCIO colors when implementing
a scene element such as an object or tag, see `py-ocio_node_2025`. You can simply run this script
in the Script Manager.

Note:
    This script requires a saved document, at least one object, and at least two materials in the
    scene to run successfully.

Note:
    The mxutils.Report decorator used in this example is a convenience function that will decorate
    the output of a function with its name. It is not necessary to use this decorator in the
    context of OCIO color management.

See Also:
    - `sdk/plugins/py-ocio_node_2025`: Example for handling OCIO colors in a `NodeData` plugin such
       as an object or tag.
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2025 MAXON Computer GmbH"
__date__ = "27/02/2025"
__license__ = "Apache-2.0 License"
__version__ = "2025.2.0"

import itertools
import struct
import os
import platform

import c4d
import maxon
import mxutils

op: c4d.BaseObject | None # The primary selected object in the scene, can be None.
doc: c4d.documents.BaseDocument # The currently active document.

def EnsureIsOcioDocument(doc: c4d.documents.BaseDocument) -> None:
    """Ensures that the given document is in OCIO color management mode.

    When the document is not in OCIO color management mode, the method will switch the document to
    OCIO color management mode and update the OCIO color spaces. This does NOT entail a conversion
    of the colors of scene elements to OCIO. One usually has to call something like this each
    time one requires/assumes a scene to be in an OCIO scene for the following operations.
    """
    mxutils.CheckType(doc, c4d.documents.BaseDocument)
    if doc[c4d.DOCUMENT_COLOR_MANAGEMENT] is not c4d.DOCUMENT_COLOR_MANAGEMENT_OCIO:
        doc[c4d.DOCUMENT_COLOR_MANAGEMENT] = c4d.DOCUMENT_COLOR_MANAGEMENT_OCIO
        doc.UpdateOcioColorSpaces()
        if c4d.threading.GeIsMainThreadAndNoDrawThread():
            c4d.EventAdd()


@mxutils.REPORT()
def CopyColorManagementSettings(doc: c4d.documents.BaseDocument) -> None:
    """Demonstrates how to copy color management settings from one document to another.
    """
    EnsureIsOcioDocument(doc)

    # Allocate a new document and copy over the settings from #doc to #newDoc. This is just a
    # convenient manner to copy all color management settings from one document to another. This
    # does NOT entail a conversion of the colors of scene elements to OCIO.
    newDoc: c4d.documents.BaseDocument = c4d.documents.BaseDocument()
    c4d.documents.BaseDocument.CopyLinearWorkflow(doc, newDoc, isMaterialPreview=False)
    print(f"Copied color management settings from '{doc}' to '{newDoc}'.")


@mxutils.REPORT()
def GetSetColorManagementSettings(doc: c4d.documents.BaseDocument) -> None:
    """Demonstrates how to get and set color management settings in a document.
    """
    EnsureIsOcioDocument(doc)

    # Print the names for all OCIO color spaces and transforms that are available in the OCIO
    # configuration file loaded by the document.
    print(f"All OCIO color space names: {doc.GetOcioColorSpaceNames()}")
    print(f"OCIO render color space names: {doc.GetOcioRenderingColorSpaceNames()}")
    print(f"OCIO view transform names: {doc.GetOcioViewTransformNames()}")
    print(f"OCIO display color space names: {doc.GetOcioDisplayColorSpaceNames()}")
    
    # Since an OCIO configuration file can contain any combination of color spaces and transforms,
    # the description IDs for the render space, display space, view transform, and view thumbnail
    # transform parameters must be dynamic IDs. I.e., you cannot just look them up in the docs.
    # They can be retrieved at runtime in the following manner.

    # We iterate over the names of all render space names (there are similar methods for the other
    # principal OCIO spaces):
    space: str
    for space in doc.GetOcioRenderingColorSpaceNames():
        # Get the index value from a space name and below the inverse operation (which we don't
        # really need in this case).
        value: int = doc.GetColorSpaceIdFromName(c4d.DOCUMENT_OCIO_RENDER_COLORSPACE, space)
        name: str = doc.GetNameFromColorSpaceId(c4d.DOCUMENT_OCIO_RENDER_COLORSPACE, value)
        print(f"The render space label '{space}' corresponds to the parameter value '{value}'.")

    # This would be the pattern to set for example the render space to a specific space name, here
    # the 'ACES2065 - 1' render space contained in the default OCIO 2.0 config file. The method
    # GetColorSpaceIdFromName() will return NOTOK to indicate unknown space labels.
    value: int = doc.GetColorSpaceIdFromName(c4d.DOCUMENT_OCIO_RENDER_COLORSPACE, "ACES2065-1")
    if value == c4d.NOTOK:
        raise ValueError("OCIO configuration does not contain an 'ACES2065 - 1' render space.")
    
    doc[c4d.DOCUMENT_OCIO_RENDER_COLORSPACE] = value
    doc.UpdateOcioColorSpaces()
    print(f"Set the render space to 'ACES2065 - 1' with value '{value}' in '{doc}'.")


@mxutils.REPORT()
def ConvertOcioColors(doc: c4d.documents.BaseDocument) -> None:
    """Demonstrates how to convert colors along the OCIO conversion paths of a document.
    """
    EnsureIsOcioDocument(doc)

    # There are two general ways how we can convert OCIO colors: 
    # 
    #   1. Within the conversion paths defined by the OCIO configuration of a document, for 
    #      example by converting a color from render to display space. 
    #   2. Within arbitrary conversion paths, as for example from an ICC profile to a render space.
    # 
    # This example covers the first case, while the following #ConvertOcioColorsArbitrarily example 
    # the covers the second case.

    # Conversions along the OCIO conversion paths are carried out with an OcioConverter, which can
    # be obtained from a document.
    converter: c4d.modules.render.OcioConverter = doc.GetColorConverter()

    # When a document is in OCIO mode, defined colors are implicitly interpreted as colors in 
    # render space (ACEScg by default). This differs from the color values and color chips the user 
    # is usually operating with, which are by default operating in sRGB.
    red: c4d.Vector = c4d.Vector(1, 0, 0)

    # Since #red implicitly defined as a render space color, we can also do pre-transformations of
    # colors. Here we interpret #red as an sRGB-2.1 value and transform it to render space. We could
    # think of this as 'importing' #red from sRGB-2.1 to the render space. For ACEScg as the render 
    # space, this will transform #red's initial value of (1, 0, 0) to (0.44, 0.09, 0.018).
    redTransformed: c4d.Vector = converter.TransformColor(
        red, c4d.COLORSPACETRANSFORMATION_OCIO_SRGB_TO_RENDERING)
    print(f"{red} --OCIO_SRGB_TO_RENDERING--> {redTransformed}")

    # There are many more transform path exposed, as for example RENDERING_TO_DISPLAY, 
    # VIEW_TO_RENDERING, and more, but they are only rarely needed for end users.

    # Finally, an OCIO converter also allows you to carry out batch conversions. Here we convert
    # the input #colors from non-linear to linear sRGB space, i.e., we shift #colors from a gamma
    # of ~2.1 to a gamma of 1.
    colors: list[c4d.Vector] = [c4d.Vector(1, 0, 0), c4d.Vector(0, 1, 0), c4d.Vector(0, 0, 1)]
    colorsTransformed: list[maxon.Vector64] = converter.TransformColors(
        colors, c4d.COLORSPACETRANSFORMATION_SRGB_TO_LINEAR)
    print(f"{colors} --OCIO_VIEW_TO_RENDERING--> {colorsTransformed}")

    # Finally, for simple color conversions, such as the conversion between linear and non-linear 
    # sRGB, we can also use c4d.utils.TransformColor() directly.
    value: c4d.Vector = c4d.Vector(1, .5, .25)
    valueLinear: c4d.Vector = c4d.utils.TransformColor(
        value, c4d.COLORSPACETRANSFORMATION_SRGB_TO_LINEAR)
    valueNonLinear: c4d.Vector = c4d.utils.TransformColor(
        valueLinear, c4d.COLORSPACETRANSFORMATION_LINEAR_TO_SRGB)

    print(f"{value} --SRGBtoLinear--> {valueLinear} --LinearToSRGB--> {valueNonLinear}")



@mxutils.REPORT()
def ConvertOcioColorsArbitrarily(doc: c4d.documents.BaseDocument) -> None:
    """Demonstrates how to convert colors between an arbitrary color space and one of the OCIO color
    spaces of a document.
    """
    EnsureIsOcioDocument(doc)

    # Get the OCIO color profiles associated with a document. The profiles for the render space,
    # display space, view transform, and view thumbnail transform are returned.
    profiles: tuple[c4d.bitmaps.ColorProfile] = doc.GetOcioProfiles()
    if len(profiles) != 4:
        raise RuntimeError("Expected to get four OCIO color profiles from the document.")
    
    # We define sRGB-2.1 as our space to convert from and the render space as the space to convert 
    # to. Instead of using one of the color profile default spaces, we could also use ColorProfile.
    # OpenProfileFromFile to load an ICC color profile file.
    inProfile: c4d.bitmaps.ColorProfile = c4d.bitmaps.ColorProfile.GetDefaultSRGB()
    outProfile: c4d.bitmaps.ColorProfile = profiles[0] # The render space profile.

    # Print the name of the profiles.
    inProfileName: str = inProfile.GetInfo(c4d.COLORPROFILEINFO_NAME)
    outProfileName: str = outProfile.GetInfo(c4d.COLORPROFILEINFO_NAME)
    print(f"{inProfileName = }")
    print(f"{outProfileName = }")

    # Instantiate a c4d.bitmaps.ColorProfileConvert to convert colors between two color profiles. 
    # The exact nature of the #PrepareTransform() call heavily depends on the used color profiles
    # and color data, we line here up the conversion between two RGB space profiles in the 8bit
    # space (COLORMODE_RGBw would be the 16bit space, and COLORMODE_RGBf the 32bit space).
    converter: c4d.bitmaps.ColorProfileConvert = c4d.bitmaps.ColorProfileConvert()
    converter.PrepareTransform(srccolormode=c4d.COLORMODE_RGB, srcprofile=inProfile, 
                               dstcolormode=c4d.COLORMODE_RGB, dstprofile=outProfile, 
                               bgr=False)
    
    # Now we are going to convert colors from the input to the output profile, in this case the
    # render space profile.

    # Here we are packing up int data as an array of bytes because #Convert expects an maxon::PIX
    # array which is an alias for an UChar array expressing 8bit integers. In Python we must use
    # struct.pack() to convert a list of integers to a byte array. For large data this will be quite
    # slow, with no good way to speed it up. 
    inColors: list[int] = [255, 0, 0, 0, 255, 0, 0, 0, 255]
    inBuffer: bytearray = bytearray(struct.pack(f"{len(inColors)}B", *inColors))

    # Allocate a nulled output buffer of the same size (which is much faster than converting a 
    # bunch of nulls with struct.pack()).
    outBuffer: bytearray = bytearray(len(inBuffer))

    # Carry out the conversion of the colors from the input profile to the output profile. The #cnt
    # tells the call how many colors are to be converted, i.e., the length of the buffers. The #skip
    # values are for respecting padding in the input and output buffers, which we do not have here.
    converter.Convert(src=inBuffer, dst=outBuffer, cnt=3, 
                      skipInputComponents=0, skipOutputComponents=0)
    
    # Unpack the output buffer and define a function that converts lists of integer values to 
    # floating point color vectors, e.g., [255, 0, 0] -> [Vector(1, 0, 0)].
    outColors: list[int] = list(struct.unpack(f'{len(outBuffer)}B', outBuffer))
    def ToVectors(colors: list[float]) -> list[c4d.Vector]:
        return [c4d.Vector(
            *(float(c)/255.0 for c in colors[i:i + 3])
        ) for i in range(0, len(colors), 3)]
    
    # Print our manual conversion result.
    print(f"{ToVectors(inColors)} --{inProfileName}_TO_{outProfileName}--> {ToVectors(outColors)}")


@mxutils.REPORT()
def ConvertScenes(doc: c4d.documents.BaseDocument) -> None:
    """Demonstrates how to convert colors stored in scene elements in an OCIO document.
    """
    EnsureIsOcioDocument(doc)
    obj: c4d.BaseObject = doc.GetFirstObject()
    if obj is None:
        raise RuntimeError("This example requires at least one object in the scene.")
    
    materials: list[c4d.BaseMaterial] = doc.GetMaterials()
    if len(materials) < 2:
        raise RuntimeError("This example requires at least two materials in the scene.")
    
    # Colors in scene elements must be converted with #SceneColorConverter. This is a bit more
    # involved than the previous examples, as we must first initialize the converter with the
    # document and the color spaces we want to convert between. The settings reflect what can be
    # done in the "Change Render Space" dialog of Cinema 4D. The conversion path shown below will
    # convert colors from the sRGB-2.1 space to the render space of #doc. 
    # 
    # Just with all other conversions, colors do not have an explicit color space. So, we could run 
    # the call below both on a scene where the colors were defined in sRGB-2.1 and the document has 
    # been then set to OCIO and a new render space (but the colors have not been converted), or on a 
    # scene where the colors were defined in OCIO (and therefore are already colors in the render 
    # space of the document). The former would be a 'correct' conversion, the latter would pile an
    # extra sRGB->RenderSpace conversion on top of the colors, and would be a 'wrong' conversion.
    converter: c4d.modules.render.SceneColorConverter = c4d.modules.render.SceneColorConverter()
    renderSpaceName: str = doc.GetActiveOcioColorSpacesNames()[0]
    converter.Init(doc, "sRGB", "scene-linear Rec.709-sRGB", renderSpaceName)

    # We can now start converting colors as defined by #converter. The conversion is carried out
    # in-place, i.e., the colors of the objects are directly converted.

    # Convert the colors of a singular scene element, here the first object in the scene. This will
    # convert everything attached to the object, i.e. , children and tags.
    if not converter.ConvertObject(doc, obj):
        print(f"Failed to color convert '{obj}'.")

    # There is also a function to batch convert multiple scene elements.
    if not converter.ConvertObjects(doc, materials):
        print(f"Failed to color convert materials '{materials}'.")

    # Finally, because a document itself is a scene element, we can also convert the colors of a
    # whole document like this.
    if not converter.ConvertObject(doc, doc):
        print(f"Failed to color convert document '{doc}'.")

    # It is also possible to convert standalone color data, such as a gradient or a color.
    gradient: c4d.Gradient = c4d.Gradient()
    gradient.InsertKnot(c4d.Vector(1, 0, 0), 1., 0, 0, 0)
    gradient.InsertKnot(c4d.Vector(0, 0, 1), 1., 1., 0, 1)

    result: c4d.Gradient | None = converter.ConvertData(gradient, treatVectorAsColor=True)
    if result is None:
        print(f"Failed to convert gradient '{gradient}'.")

    print(f"{result.GetKnot(0) = }")
    print(f"{result.GetKnot(1) = }")

    # When #doc is the active document, and we want to be the changes to be reflected in the UI, we
    # must call EventAdd() to update the UI.
    c4d.EventAdd()


@mxutils.REPORT()
def GetSetColorValuesInSceneElements(doc: c4d.documents.BaseDocument) -> None:
    """Demonstrates how to get and set color values in scene elements in an OCIO document.
    """
    EnsureIsOcioDocument(doc)

    converter: c4d.modules.render.OcioConverter = doc.GetColorConverter()

    # When a document is in OCIO mode, all colors in scene elements are by default written and read 
    # as render space colors. The default material color of document is for example expressed as such
    # render space value. This differs visually and numerically from the sRGB-2.1 values users usually
    # operate with. So, when you set the value (1, 0, 0) in the UI of a scene element, that is not 
    # the value that will be factually written as data.
    defaultColor: c4d.Vector = doc[c4d.DOCUMENT_DEFAULTMATERIAL_COLOR]

    # So, when we write a color literal in code, this is also not the same value as if a user would 
    # dial in that value in an sRGB-2.1 color chip UI.
    doc[c4d.DOCUMENT_DEFAULTMATERIAL_COLOR] = c4d.Vector(1, 0, 0)

    # This can be sidestepped by either pre-transforming written, or post-transforming read values,
    # here we write for example pure red in sRGB-2.1 space as a render space color.
    doc[c4d.DOCUMENT_DEFAULTMATERIAL_COLOR] = converter.TransformColor(
        c4d.Vector(1, 0, 0), c4d.COLORSPACETRANSFORMATION_OCIO_SRGB_TO_RENDERING)
    
    # For this specific case, writing a color value as an sRGB-2.1 value, there is also a special
    # flag for SetParameter which carries out the conversion for us.
    if not doc.SetParameter(
        c4d.DOCUMENT_DEFAULTMATERIAL_COLOR, c4d.Vector(1, 0, 0), c4d.DESCFLAGS_SET_COLOR_SRGB):
        raise KeyError(f"Failed to write to DOCUMENT_DEFAULTMATERIAL_COLOR.")
    
    # This all might seem a bit confusing at first, but the general rule is:
    #
    #   - Just operate in render space, that is the whole purpose of OCIO to offer a computational 
    #     space which you can just use without thinking about conversions. That is the same as it 
    #     has been before in the old classic color management system of Cinema 4D, where linear
    #     workflow was the default. The only difference is that the render space is now ACEScg
    #     where the computational space was linear sRGB in the old system.
    #   - Only when one must match legacy data or otherwise inputs in sRGB, imagine a customer
    #     giving you a list of sRGB brand color values that you want to import from a JSOn file, 
    #     then one must pre-transform values to match that sRGB value in OCIO space.


@mxutils.REPORT()
def GetSetBitmapOcioProfiles(doc: c4d.documents.BaseDocument) -> None:
    """Demonstrates how to handle OCIO color profiles in bitmaps.
    """
    EnsureIsOcioDocument(doc)

    # Create a bitmap with a red to blue gradient.
    bitmap: c4d.bitmaps.BaseBitmap = c4d.bitmaps.BaseBitmap()
    if bitmap.Init(512, 128) != c4d.IMAGERESULT_OK:
        raise RuntimeError("Could not initialize the bitmap.")
    
    for x, y in itertools.product(range(512), range(128)):
        color: c4d.Vector = c4d.utils.MixVec(c4d.Vector(1, 0, 0), c4d.Vector(0, 0, 1), x / 512)
        bitmap.SetPixel(x, y, int(color.x * 255), int(color.y * 255), int(color.z * 255))

    # Clone the bitmap.
    clone: c4d.bitmaps.BaseBitmap = bitmap.GetClone()
    if clone is None:
        raise RuntimeError("Could not clone the bitmap.")
    
    # Get the OCIO profiles from the document. Even though our document is in OCIO mode, Cinema 4D
    # has no idea that our bitmaps shall be OCIO bitmaps and initializes them without OCIO profiles 
    # attached.
    profiles: tuple[c4d.bitmaps.ColorProfile] = doc.GetOcioProfiles()
    if len(profiles) != 4:
        raise RuntimeError("Expected to get four OCIO color profiles from the document.")
    
    renderProfile, displayProfile, viewProfile, _ = profiles
    
    # This is how a render engine would setup a bitmap in order to be displayed in the picture 
    # viewer, i.e., the render, display, and view profiles are written into their respective slots.
    bitmap.SetColorProfile(renderProfile, c4d.COLORPROFILE_INDEX_RENDERSPACE)
    bitmap.SetColorProfile(displayProfile, c4d.COLORPROFILE_INDEX_DISPLAYSPACE)
    bitmap.SetColorProfile(viewProfile, c4d.COLORPROFILE_INDEX_VIEW_TRANSFORM)

    # But we can do something like this, where we write the render space profile to all the profiles
    # of the bitmap, making the display space and view transform the null transform, i.e., the image
    # will be displayed in raw render space colors.
    clone.SetColorProfile(renderProfile, c4d.COLORPROFILE_INDEX_RENDERSPACE)
    clone.SetColorProfile(renderProfile, c4d.COLORPROFILE_INDEX_DISPLAYSPACE)
    clone.SetColorProfile(renderProfile, c4d.COLORPROFILE_INDEX_VIEW_TRANSFORM)

    # Display the bitmaps in the Picture Viewer.
    c4d.bitmaps.ShowBitmap(bitmap, "OCIO")
    c4d.bitmaps.ShowBitmap(clone, "RAW")
    
if __name__ == "__main__":
    CopyColorManagementSettings(doc)
    GetSetColorManagementSettings(doc)
    ConvertOcioColors(doc)
    ConvertOcioColorsArbitrarily(doc)
    ConvertScenes(doc)
    GetSetColorValuesInSceneElements(doc)
    GetSetBitmapOcioProfiles(doc)

    c4d.EventAdd()
