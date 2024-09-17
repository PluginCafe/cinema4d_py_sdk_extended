"""Demonstrates how to handle colors in scene elements in the context then OpenColorIO (OCIO)
standard.

Since Cinema 4D 2025, OCIO has become the default color management system in Cinema 4D. This code
examples highlights how to write a scene element plugin, an object, deformer, tag, shader, etc.,
that is OCIO aware at the example of an generator object plugin. Highlighted in particular are the
color initlization behavior of NodeData.Init() and the color handling drawing methods such as
ObjectData.Draw().

Class or methods highlighted:
    - c4d.plugins.NodeData.Init()
    - c4d.plugins.NodeData.Message()
    - c4d.plugins.ObjectData.Draw()
    - c4d.BaseDraw.SetPen()
"""
__copyright__ = "Copyright 2022, MAXON Computer"
__author__ = "Ferdinand Hoppe"
__date__ = "13/09/2024"
__license__ = "Apache-2.0 license"

import sys
import os

import c4d
import maxon


class OcioNode2025(c4d.plugins.ObjectData):
    """Realizes a NodeData plugin that is meant to operate in OCIO enabled scenes.
    """
    # The unique ID of the plugin, you must obtain your own ID from www.developers.maxon.net for
    # your plugins. Ignoring this will lead to plugin ID conflicts and the plugin will not load.
    ID_PLUGIN: int = 1064267

    def __init__(self):
        """Initializes the plugin instance.
        """
        #: The bitmap used to draw the texture in the Draw() method. We preload the texture in the
        # PreloadTextures() method to avoid loading it in the Draw() method.
        self._bitmap: c4d.bitmaps.BaseBitmap | None = None
    
    def Init(self, node: c4d.BaseObject, isCloneInit: bool = False) -> bool:
        """Called by Cinema 4D to let the node initialize its parameters and internal data.

        This function is called more often than one might expect, as Cinema 4D reinitializes
        nodes. For heavy pre-calculations, the message `c4d.MSG_MENUPREPARE` is the better choice, 
        as it will only run once. You then also have to override NodeData.CopyTo() to copy over 
        internal data in a copy event.

        Args:
            node (c4d.GeListNode): The instance of the plugin node to be initialized.
            isCloneInit (bool): True if Cinema 4D cloned this node from another one.

        Returns:
            bool: True on success, otherwise False.
        """
        # Abort the node creation by returning False when #node or the data instance is None and
        # just exit the node initialization when this is a cloning event, in this case Cinema 4D
        # will copy the data from the original node.
        if not node or node.GetDataInstance() is None:
            return False
        
        # We are a little bit wasteful here and preload textures even for a cloning event, as this 
        # could also be solved with CopyTo() or even be stored on the class instance level.
        self.PreloadTextures()
        if isCloneInit:
            return True

        # Set the color attribute of the node to red, in 2025.0.0, this will be interpreted as an 
        # sRGB-2.2 color, even when the scene has OCIO color management enabled and the render space is
        # not sRGB-2.2.
        bc: c4d.BaseContainer = node.GetDataInstance()
        self.InitAttr(node, c4d.Vector, c4d.OCIO_NODE_2025_COLOR)
        bc.SetVector(c4d.OCIO_NODE_2025_COLOR, c4d.Vector(1.0, 0.0, 0.0))

        return True
    

    def PreloadTextures(self) -> bool:
        """Loads the texture which is drawn in the Draw() method of this node.

        This is a custom method which is not part of the NodeData interface. 
        """
        # We should avoid loading textures inside a Draw() method, as this can lead to performance
        # problems and other issues, this especially applies when we are loading the texture from an
        # asset database.

        # Attempt to get the "UV Test Grid.png" from the default asset database of Cinema 4D.
        if not maxon.AssetDataBasesInterface.WaitForDatabaseLoading():
            return False
        
        assetUrl: maxon.Url = maxon.Url("asset:///file_5b6a5fe03176444c")
        asset: maxon.AssetDescription = maxon.AssetInterface.ResolveAsset(
            assetUrl, maxon.AssetInterface.GetUserPrefsRepository())
        if asset.IsNullValue():
            raise ValueError("Could not resolve asset for 'UV Test Grid.png'.")
        
        # Load the bitmap from the asset.
        imgUrl: maxon.Url = maxon.AssetInterface.GetAssetUrl(asset, True)
        bmp: c4d.bitmaps.BaseBitmap = c4d.bitmaps.BaseBitmap()
        if bmp is None:
            raise MemoryError("Could not allocate bitmap.")
        
        if bmp.InitWith(imgUrl.GetUrl())[0] != c4d.IMAGERESULT_OK:
            raise ValueError("Could not init bitmap from file.")
        
        # In Python, we currently have neither access to the OCIO color profiles of a bitmap (which
        # are non-functional for viewport drawing operations anyway at the moment). But we could
        # pre-transform the bitmap from another color space to sRGB-2.2 with 
        # c4d.bitmaps.ColorProfileConvert if we wanted to see the bitmap interpreted as a specific
        # color space.

        # Store the bitmap in the instance of the plugin node.
        self._bitmap = bmp

        return True
    
    
    def Message(self, node: c4d.BaseObject, mid: int, mdata: c4d.BaseContainer) -> any:
        """Called by Cinema 4D to notify the node of a special event.

        Args:
            node (c4d.BaseObject): The instance of the plugin node.
            mid (int): The type of message which is being sent.
            data (c4d.BaseContainer): The message data which is accompanying #mid.

        Returns:
            any: Depends on the message type, most of the time True.
        """
        # To prevent node color values being interpreted as sRGB-2.2, we must overwrite them when
        # MSG_MENUPREPARE is being emitted.
        if mid == c4d.MSG_MENUPREPARE:
            # Force the color to be (1, 0, 0) in render space.
            node[c4d.OCIO_NODE_2025_COLOR] = c4d.Vector(1.0, 0.0, 0.0)
            return True
        return True


    def Draw(self, op: c4d.BaseObject, drawpass: int, bd: c4d.BaseDraw, bh: c4d.plugins.BaseDrawHelp) -> int:
        """Called by Cinema 4D to draw the object in the viewport.
        """
        # Get out when we are in a draw pass we do not want to draw into, or when we are missing data.
        if drawpass != c4d.DRAWPASS_HANDLES and drawpass != c4d.DRAWPASS_OBJECT:
            return super().Draw(op, drawpass, bd, bh)
        if not bd or not bh or not op or not self._bitmap:
            return c4d.DRAWRESULT_SKIP
        
        # Make sure that there is a polygonal cache and a data container for our node.
        cache: c4d.BaseObject = op.GetCache()
        poly: c4d.PolygonObject = cache if cache and cache.GetType() == c4d.Opolygon else None
        bc: c4d.BaseContainer = op.GetDataInstance()
        if not poly or not bc:
            return c4d.DRAWRESULT_SKIP
        
        # Get the bounding box radius of the object as we will need it later.
        bboxRadius: c4d.Vector = poly.GetRad()

        # Cinema 4D asks us to draw handles for our object, we are going to draw a (non-functional)
        # handle on each point of the object in the color defined by the node data. See other
        # ObjectData examples for more information on how to implement handles.
        if drawpass == c4d.DRAWPASS_HANDLES:
            # When we want to draw a color value from our node's data container, we should draw it 
            # with SET_PEN_USE_PROFILE_COLOR. This will be the correct choice in all cases except 
            # for:
            #
            # 1. The document is in OCIO mode, and we want explicitly to draw a color interpreted as
            #    an sRGB-2.2 value instead of a render space value.
            # 2. The document is in Basic color management mode but linear workflow is enabled and 
            #    we again want to draw a color as an sRGB-2.2 value.
            #
            # In both cases we must pass the flag 0 to SetPen, the default. SET_PEN_USE_PROFILE_COLOR
            # on the other hand will draw as a render space color in OCIO mode, and as a linear sRGB
            # in basic color management mode with linear workflow enabled.
            #
            # When a document is in basic color management mode with linear workflow disabled, this
            # flag makes no difference, since both color spaces are then the same.
            bd.SetPen(bc.GetVector(c4d.OCIO_NODE_2025_COLOR), c4d.SET_PEN_USE_PROFILE_COLOR)

            # Set the drawing matrix the coordinate system of the object and the point size to 20.
            bd.SetMatrix_Matrix(op, op.GetMg())
            bd.SetPointSize(20)

            # Draw a handle on each point of the object in the color defined by the node's data 
            # container.
            for p in poly.GetAllPoints():
                bd.DrawHandle(p, c4d.DRAWHANDLE_CUSTOM, 0)
            
            # Colors from the world settings should be drawn in this manner at the moment, here we 
            # draw a line along the local y-axis of the object in the color y-axis color from the 
            # world settings. We draw here in sRGB as this is the best approximation we have at the
            # moment in Python, this assume that the display device is sRGB-2.2.
            bd.SetPen(c4d.GetViewColor(c4d.VIEWCOLOR_WYAXIS), 0)
            bd.DrawLine(c4d.Vector(0, -bboxRadius.y, 0), c4d.Vector(0, bboxRadius.y, 0), 0)
        
        # Now we are going to draw a texture in world space, i.e., a texture that pans, rotates, and
        # scales with the active camera. It is important to draw textures which are drawn with
        # SetMatrix_Matrix in the object drawpass, other draw passes will not work as expected.
        if drawpass == c4d.DRAWPASS_OBJECT and self._bitmap:
            # We again set the drawing matrix to the local coordinate system of the object.
            bd.SetMatrix_Matrix(op, op.GetMg())

            # Set up the points and UVs for a texture drawn at 50% of the object's bounding box radius
            # directly onto the object.
            texRadius: c4d.Vector = bboxRadius * 0.5
            texPoints: list[c4d.Vector] = [
                c4d.Vector(-texRadius.x,  texRadius.y, 0),
                c4d.Vector(texRadius.x,  texRadius.y, 0),
                c4d.Vector(texRadius.x, -texRadius.y, 0),
                c4d.Vector(-texRadius.x, -texRadius.y, 0)
            ]
            texUVs: list[c4d.Vector] = [
                c4d.Vector(0, 0, 0),
                c4d.Vector(1, 0, 0),
                c4d.Vector(1, 1, 0),
                c4d.Vector(0, 1, 0)
            ]
            texColors: list[c4d.Vector] = [c4d.Vector(1)] * 4
            texNormals: list[c4d.Vector] = [c4d.Vector(0, 0, 1)] * 4

            # Set the z-offset of the following drawing operation so that we draw over polygons (0),
            # points (2), and edges (4) and then draw the texture. We again use here USE_PROFILE_COLOR.
            bd.LineZOffset(5)
            bd.DrawTexture(self._bitmap, texPoints, texColors, texNormals, texUVs, 4,
                c4d.DRAW_ALPHA_NORMAL, c4d.DRAW_TEXTUREFLAGS_USE_PROFILE_COLOR)
            
        # Draw the two textures in screen space to the left of the object. Textures in screen 
        # space usually should be drawn in the handles #drawpass, as textures in the object pass 
        # are also visible when the object is not selected. And permanently visible textures 
        # plus screen space, i.e., textures that do do not pan, rotate, or scale with the camera, 
        # would be very distracting. If we would draw in the object draw pass, this would also 
        # mean that the handles could overlap with these two screen space textures (which is 
        # likely not what we want). When we draw in the handles draw pass, the drawing order 
        # will determine if the texture is drawn over or under the handles. Since we draw the 
        # handles above, and the textures below, the textures will be drawn over the handles 
        # in this case.
        if drawpass == c4d.DRAWPASS_HANDLES and self._bitmap:
            # Get the left, top, and bottom safe frame offsets for the viewport (the black bars which
            # are drawn for viewports which do not match the aspect ratio of the render output).
            safeFrame: dict = bd.GetSafeFrame()
            topSafeOffset: int = safeFrame.get("ct", 0)
            bottomSafeOffset: int = safeFrame.get("cb", 0)
            leftSafeOffset: int = safeFrame.get("cl", 0)

            # Calculate where we have to place our two textures so that they fit nicely into the left
            # side of the viewport without overlapping with the safe frame borders.
            margin: int = 25
            safeViewPortHeight: int = bottomSafeOffset - topSafeOffset - 2 * margin
            textureHeight: int = int(float(safeViewPortHeight) * .5) - margin
            if textureHeight < 1:
                return c4d.DRAWRESULT_SKIP
            
            # The uv coordinates we are going to use for both textures.
            texUVs: list[c4d.Vector] = [
                c4d.Vector(0, 0, 0),
                c4d.Vector(1, 0, 0),
                c4d.Vector(1, 1, 0),
                c4d.Vector(0, 1, 0)
            ]
            texColors: list[c4d.Vector] = [c4d.Vector(1)] * 4
            texNormals: list[c4d.Vector] = [c4d.Vector(0, 0, 1)] * 4

            # Draws a texture with a label below it, we are going to use this to draw both textures.
            def drawTextureWithLabel(i: int, flags: int):
                # The four points of the rectangle in which we are going to draw the texture.
                xa = leftSafeOffset + margin
                xb = xa + textureHeight
                ya = topSafeOffset + margin + i * (textureHeight + margin)
                yb = ya + textureHeight

                points: list[c4d.Vector] = [
                    c4d.Vector(xa, ya, 0),
                    c4d.Vector(xb, ya, 0),
                    c4d.Vector(xb, yb, 0),
                    c4d.Vector(xa, yb, 0)
                ]

                # Check if we draw the texture in profile color mode or not.
                isProfile = ((flags & c4d.DRAW_TEXTUREFLAGS_USE_PROFILE_COLOR) == 
                             c4d.DRAW_TEXTUREFLAGS_USE_PROFILE_COLOR)

                # Draw the texture and a label for the flag below it.
                bd.DrawTexture(self._bitmap, points, texColors, texNormals, texUVs, 4, 
                               c4d.DRAW_ALPHA_NORMAL, flags)
                bd.DrawHUDText(xa, yb, "USE_PROFILE_COLOR" if isProfile else "NONE")

            # Set the drawing matrix to screen space and draw the texture once in profile color mode 
            # and once in normal mode. The former is usually the best choice for drawing textures, as
            # it will draw the texture as it would be seen in render output (if the texture would be
            # part of it).
            bd.SetMatrix_Screen()
            drawTextureWithLabel(0, c4d.DRAW_TEXTUREFLAGS_USE_PROFILE_COLOR)
            drawTextureWithLabel(1, c4d.DRAW_TEXTUREFLAGS_NONE)

        return c4d.plugins.ObjectData.Draw(self, op, drawpass, bd, bh)


    def GetVirtualObjects(self, op: c4d.BaseObject, hh: object) -> c4d.BaseObject:
        """Called by Cinema 4D to generate the polygonal cache of the object.

        Args:
            op (c4d.BaseObject): The instance of the plugin node.
            hh (object): The hierarchy helper for the object.

        Returns:
            c4d.BaseObject: The polygonal cache of the object.
        """
        # Attempt to get an exiting cache and return it when it is valid.
        if not op or not hh:
            return None
        
        isDirty: bool = op.CheckCache(hh) or op.IsDirty(c4d.DIRTYFLAGS_DATA)
        if not isDirty:
            return op.GetCache()
        
        # Build a simple quad polygon and return it as the cache of the generator.
        result: c4d.PolygonObject = c4d.PolygonObject(4, 1)
        if not result:
            return c4d.BaseObject(c4d.Onull)
        
        diameter: float = 200
        points: list[c4d.Vector] = [
            c4d.Vector(-diameter, -diameter, 0),
            c4d.Vector(diameter, -diameter, 0),
            c4d.Vector(diameter, diameter, 0),
            c4d.Vector(-diameter, diameter, 0)
        ]

        result.SetAllPoints(points)
        result.SetPolygon(0, c4d.CPolygon(3, 2, 1, 0))

        return result
 

# Register the plugin when Cinema 4D tries to execute this file.
if __name__ == "__main__":
    if not c4d.plugins.RegisterObjectPlugin(
        id=OcioNode2025.ID_PLUGIN, str="Py-OCIO Node 2025", g=OcioNode2025, 
        description="oocionode2025", icon=None, info=c4d.OBJECT_GENERATOR):
        raise RuntimeError("Failed to register the OCIO Node 2025 plugin.")

