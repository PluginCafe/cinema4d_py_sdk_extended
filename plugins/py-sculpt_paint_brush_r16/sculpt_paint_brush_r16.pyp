"""
Copyright: MAXON Computer GmbH
Author: Kent Barber

Description:
    - Brush Tool, rasterize the stencil onto the polygons touched by the brush. You will need an active stencil for the brush to work.
    - Illustrates the ability to access the stencil for a brush and also how to access the bodypaint layer to apply paint.

Notes:
    - This brush is very slow, and mainly done for demonstration purpose.
    - The code used in this code uses the same approach of rasterization algorithm described from Josh Beams website.
        http://joshbeam.com/articles/triangle_rasterization/

Class/method highlighted:
    - c4d.plugins.SculptBrushToolData
    - SculptBrushToolData.GetToolPluginId()
    - SculptBrushToolData.GetResourceSymbol()
    - SculptBrushToolData.PostInitDefaultSettings()
    - SculptBrushToolData.ApplyDab()
    - c4d.modules.bodypaint.PaintLayerBmp
    - PaintLayerBmp.GetPixelCnt()
    - PaintLayerBmp.SetPixelCnt()

Compatible:
    - Win / Mac
    - R16, R17, R18, R19, R20, R21
"""

import c4d
import math

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1031348 

# Values must match with the header file
IDS_PYTHON_BRUSH_PAINT = 10000


class Edge(object):
    """ Represents an Edge"""

    def __init__(self, color1, x1, y1, color2, x2, y2):
        if y1 < y2:
            self.color1 = color1
            self.x1 = x1
            self.y1 = math.floor(y1)
            self.color2 = color2
            self.x2 = x2
            self.y2 = math.ceil(y2)
        else:
            self.color1 = color2
            self.x1 = x2
            self.y1 = math.floor(y2)
            self.color2 = color1
            self.x2 = x1
            self.y2 = math.ceil(y1)


class Span(object):
    """ Represents a Span"""

    def __init__(self, color1, x1, color2, x2):
        if x1 < x2:
            self.color1 = color1
            self.x1 = x1
            self.color2 = color2
            self.x2 = x2
        else:
            self.color1 = color2
            self.x1 = x2
            self.color2 = color1
            self.x2 = x1


class PaintBrushToolHelper(object):

    @staticmethod
    def DrawSpan(dab, bmp, span, y):
        """
        Draws a span in the given bmp
        :param dab: The brush dab data.
        :type dab: c4d.modules.sculpting.BrushDabData
        :param bmp: The bitmap to draw in
        :type bmp: c4d.modules.bodypaint.PaintLayerBmp
        :param span: The span to draw
        :type span: Span
        :param y: height of the span to draw
        :type y: int
        """
        xdiff = math.ceil(span.x2) - math.floor(span.x1)
        if xdiff == 0:
            return

        colorDiff = span.color2 - span.color1
        factor = 0.0
        factorStep = 1.0 / float(xdiff)

        if span.x1 < 0 or span.x2 < 0:
            return

        if span.x1 > bmp.GetBw() or span.x2 > bmp.GetBw():
            return

        currentPixel = 0
        startPixel = int(math.floor(span.x1))
        endPixel = int(math.ceil(span.x2))

        fillTool = dab.IsFillTool()

        # Creates a byte sequence buffer for 3 bytes
        numPixels = endPixel - startPixel
        sq = c4d.storage.ByteSeq(None, numPixels*c4d.COLORBYTES_RGB)

        # Retrieves the current colors of the bitmap
        flag = c4d.PIXELCNT_NONE if c4d.GetC4DVersion() > 20000 else c4d.PIXELCNT_0
        bmp.GetPixelCnt(startPixel, y, numPixels, sq, c4d.COLORMODE_RGB, flag)

        for x in range(startPixel, endPixel):
            # Retrieves the location on the object for this part of the triangle that we are rasterizing
            pos = span.color1 + (colorDiff * factor)

            # Retrieves the stencil color that should be applied to the pixel at this position
            stencilData = dab.GetStencilColor(pos)
            stencilCol = stencilData["color"]

            # Retrieves the falloff for the brush for this position
            falloff = 1.0
            if fillTool is False:
                falloff = dab.GetBrushFalloffFromPos(pos)

            # Retrieves the rgb colors from the byte sequence
            r = ord(sq[currentPixel])
            g = ord(sq[currentPixel+1])
            b = ord(sq[currentPixel+2])

            # Calculates the new color by multiplying the color (0.0 to 1.0) by 255
            newR = stencilCol.x * 255.0
            newG = stencilCol.y * 255.0
            newB = stencilCol.z * 255.0

            # Blends the current and new color together using the falloff
            mixR = r * (1.0-falloff) + newR * falloff
            mixG = g * (1.0-falloff) + newG * falloff
            mixB = b * (1.0-falloff) + newB * falloff

            # Retrieves the data back into the byte sequence so that we can set it on the bitmap agian
            sq[currentPixel] = chr(int(mixR))
            sq[currentPixel+1] = chr(int(mixG))
            sq[currentPixel+2] = chr(int(mixB))

            currentPixel = currentPixel + 3

            factor += factorStep

        # Defines the new color of this pixel
        flag = c4d.PIXELCNT_NONE if c4d.GetC4DVersion() > 20000 else c4d.PIXELCNT_0
        bmp.SetPixelCnt(startPixel, y, numPixels, sq, c4d.COLORBYTES_RGB, c4d.COLORMODE_RGB, flag)

    @staticmethod
    def DrawSpansBetweenEdges(dab, bmp, e1, e2):
        """
        :param dab: The brush dab data.
        :type dab: c4d.modules.sculpting.BrushDabData
        :param bmp: The bitmap to draw in
        :type bmp: c4d.modules.bodypaint.PaintLayerBmp
        :param e1: The first edge
        :type e1: Edge
        :param e2: The second edge
        :type e2: Edge
        :return:
        """
        # Calculates difference between the y coordinates of the first, second edge and return if 0
        e1ydiff = float(e1.y2 - e1.y1)
        e2ydiff = float(e2.y2 - e2.y1)
        if e1ydiff == 0.0 or e2ydiff == 0.0:
            return

        # Calculates differences between the x coordinates and colors of the points of the edges
        e1xdiff = float(e1.x2 - e1.x1)
        e2xdiff = float(e2.x2 - e2.x1)
        e1pointdiff = e1.color2 - e1.color1
        e2pointdiff = e2.color2 - e2.color1

        # Calculates factors to use for interpolation with the edges and the step values to increase them after drawing each span
        factor1 = float(e2.y1 - e1.y1) / e1ydiff
        factorStep1 = 1.0 / e1ydiff
        factor2 = 0.0
        factorStep2 = 1.0 / e2ydiff

        # Loops through the lines between the edges and draw spans
        for y in range(int(e2.y1), int(e2.y2)):
            # Creates and draw span
            span = Span(e1.color1 + (e1pointdiff * factor1), e1.x1 + int(e1xdiff * factor1), e2.color1 + (e2pointdiff * factor2), e2.x1 + int(e2xdiff * factor2))
            PaintBrushToolHelper.DrawSpan(dab, bmp, span, y)

            # Increases factors
            factor1 += factorStep1
            factor2 += factorStep2

    @staticmethod
    def DrawTriangle(dab, bmp, color1, x1, y1, color2, x2, y2, color3, x3, y3):
        """
        Draws a Triangle into the passed PaintLayerBmp.
        :param dab: The brush dab data.
        :type dab: c4d.modules.sculpting.BrushDabData
        :param bmp: The bitmap to draw in
        :type bmp: c4d.modules.bodypaint.PaintLayerBmp
        :param color1: Color from (0,1) of the first point
        :type color1: c4d.Vector
        :param x1: X position in uv space of the first point
        :type x1: Union[float, int]
        :param y1: Y position in uv space of the first point
        :type y1: Union[float, int]
        :param color2: Color from (0,1) of the second point
        :type color2: c4d.Vector
        :param x2: X position in uv space of the second point
        :type x2: Union[float, int]
        :param y2: Y position in uv space of the second point
        :type y2: Union[float, int]
        :param color3: Color from (0,1) of the third point
        :type color3: c4d.Vector
        :param x3: X position in uv space of the third point
        :type x3: Union[float, int]
        :param y3: Y position in uv space of the third point
        :type y3: Union[float, int]
        """
        # Creates edges for the triangle
        edges = [
            Edge(color1, round(x1), round(y1), color2, round(x2), round(y2)),
            Edge(color2, round(x2), round(y2), color3, round(x3), round(y3)),
            Edge(color3, round(x3), round(y3), color1, round(x1), round(y1))
        ]
        maxLength = 0
        longEdge = 0

        # Finds edge with the greatest length in the y axis
        for i in range(0, 3):
            length = edges[i].y2 - edges[i].y1
            if length > maxLength:
                maxLength = length
                longEdge = i

        shortEdge1 = (longEdge + 1) % 3
        shortEdge2 = (longEdge + 2) % 3

        # Draws spans between edges,
        # The long edge can be drawn with the shorter edges to draw the full triangle
        PaintBrushToolHelper.DrawSpansBetweenEdges(dab, bmp, edges[longEdge], edges[shortEdge1])
        PaintBrushToolHelper.DrawSpansBetweenEdges(dab, bmp, edges[longEdge], edges[shortEdge2])


class PaintBrushTool(c4d.plugins.SculptBrushToolData, PaintBrushToolHelper):
    """Inherit from SculptBrushToolData to create your own sculpting tool"""

    def GetToolPluginId(self):
        """
        Called by Cinema 4D, to know the plugin ID of this tool.
        :return: The unique id for the tool plugin as obtained from www.plugincafe.com
        :rtype: int
        """
        return PLUGIN_ID

    def GetResourceSymbol(self):
        """
        Called by Cinema 4D, to know the resource to be used for this tool.
        :return: The resource name of the tool
        :rtype: str
        """
        return "pythonpaintbrush"

    def ApplyDab(self, dab):
        """
        Called by Cinema 4D, to modify the sculpt object.
        Implement the brush functionality in this method
        :param dab: The brush dab data.
        :type dab: c4d.modules.sculpting.BrushDabData
        """
        # Retrieves the strength applied
        strength = dab.GetBrushStrength()
        if strength == 0:
            return True

        # Retrieves polygons count affected
        polyCount = dab.GetPolyCount()

        # Retrieves polygons objects affected
        polyObj = dab.GetPolygonObject()

        # Retrieves the first uvw tag from the object
        uvs = polyObj.GetTag(c4d.Tuvw)
        if uvs is None:
            return False

        # Retrieves the selected texture in bodypaint
        texture = c4d.modules.bodypaint.PaintTexture.GetSelectedTexture()
        if texture is None:
            return False

        # Retrieves the selected layer
        layer = texture.GetActive()
        if layer is None:
            return False

        # Retrieves the PaintLayerBmp stored in the layer
        paintLayerBmp = layer.ToPaintLayerBmp()
        if paintLayerBmp is None:
            return False

        # Retrieves the size
        width = paintLayerBmp.GetBw()
        height = paintLayerBmp.GetBh()

        minX = width
        minY = height
        maxX = 0
        maxY = 0

        # Loops over very polygon for this dab and rasterize the stencil to it.
        for a in range(0, polyCount):
            # Retrieves the index of the point on the PolygonObject.
            polyData = dab.GetPolyData(a)
            polyIndex = polyData["polyIndex"]
            poly = polyObj.GetPolygon(polyIndex)
            polyUVs = uvs.GetSlow(polyIndex)

            pointA = polyObj.GetPoint(poly.a)
            pointB = polyObj.GetPoint(poly.b)
            pointC = polyObj.GetPoint(poly.c)
            pointD = polyObj.GetPoint(poly.d)

            destA = polyUVs["a"]
            destB = polyUVs["b"]
            destC = polyUVs["c"]
            destD = polyUVs["d"]

            destA.x *= width
            destA.y *= height
            destB.x *= width
            destB.y *= height
            destC.x *= width
            destC.y *= height
            destD.x *= width
            destD.y *= height

            # Calculates the region touched by the brush
            if destA.x > maxX:
                maxX = destA.x
            if destB.x > maxX:
                maxX = destB.x
            if destC.x > maxX:
                maxX = destC.x
            if destD.x > maxX:
                maxX = destD.x

            if destA.y > maxY:
                maxY = destA.y
            if destB.y > maxY:
                maxY = destB.y
            if destC.y > maxY:
                maxY = destC.y
            if destD.y > maxY:
                maxY = destD.y

            if destA.x < minX:
                minX = destA.x
            if destB.x < minX:
                minX = destB.x
            if destC.x < minX:
                minX = destC.x
            if destD.x < minX:
                minX = destD.x

            if destA.y < minY:
                minY = destA.y
            if destB.y < minY:
                minY = destB.y
            if destC.y < minY:
                minY = destC.y
            if destD.y < minY:
                minY = destD.y

            self.DrawTriangle(dab, paintLayerBmp,
                pointA, destA.x, destA.y,
                pointB, destB.x, destB.y,
                pointC, destC.x, destC.y)

            if poly.c != poly.d:
                self.DrawTriangle(dab, paintLayerBmp,
                    pointA, destA.x, destA.y,
                    pointC, destC.x, destC.y,
                    pointD, destD.x, destD.y)

        # Refreshes the paint layer, so the viewport is updated
        paintLayerBmp.UpdateRefresh(int(minX), int(minY), int(maxX), int(maxY), c4d.UPDATE_STD)
        return True


if __name__ == "__main__":
    # Defines global parameter for the brush (how the brush should act)
    params = c4d.modules.sculpting.SculptBrushParams()

    # Registers the tool brush plugin
    c4d.plugins.RegisterSculptBrushPlugin(id=PLUGIN_ID,
                                          str="Python Paint Brush",
                                          info=0,
                                          icon=None,
                                          help="Python Paint Brush",
                                          sculptparams=params,
                                          dat=PaintBrushTool())
