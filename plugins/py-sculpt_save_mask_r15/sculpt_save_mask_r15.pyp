"""
Copyright: MAXON Computer GmbH
Author: Kent Barber

Description:
    - Command, rasterizing(baking) the mask data to a bitmap using the first found UV tag on the sculpt object.
    - Illustrates the ability to access the mask data on a sculpt object.
    
Notes:
    - The command is a bit slow due to rasterization, and mainly done for demonstration purpose.
    - The code used in this code uses the same approach of rasterization algorithm described from Josh Beams website.
        http://joshbeam.com/articles/triangle_rasterization/

Class/method highlighted:
    - c4d.plugins.CommandData
    - CommandData.Execute()
    - c4d.modules.sculpting.GetSelectedSculptObject()
    - c4d.modules.sculpting.SculptObject
    - SculptObject.GetCurrentLayer()
    - c4d.modules.sculpting.SculptLayer
    - SculptLayer.GetMask()

"""
import c4d
import math


PLUGIN_ID = 1031644


class Edge(object):
    """Represents an Edge"""

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
    """Represents a Span"""

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


class MaskImageCmdHelper(object):

    @staticmethod
    def DrawSpan(bmp, span, y):
        """Draws a span in the given bmp.

        Args:
            bmp (c4d.bitmaps.BaseBitmap): The bitmap to draw in
            span (Span): The span to draw
            y (int): height of the span to draw
        """
        xdiff = math.ceil(span.x2) - math.floor(span.x1)
        if xdiff == 0:
            return

        colordiff = span.color2 - span.color1
        factor = 0.0
        factorStep = 1.0 / float(xdiff)

        if span.x1 < 0 or span.x2 < 0:
            return

        if span.x1 > bmp.GetBw() or span.x2 > bmp.GetBw():
            return

        # Draw each pixels
        for x in range(int(math.floor(span.x1)), int(math.ceil(span.x2))):
            col = span.color1 + (colordiff * factor)
            bmp.SetPixel(x, y, int(col.x * 255), int(col.y * 255), int(col.z * 255))
            factor += factorStep

    @staticmethod
    def DrawSpansBetweenEdges(bmp, e1, e2):
        """

        Args:
            bmp (c4d.bitmaps.BaseBitmap): The bitmap to draw in
            e1 (Edge): The first edge
            e2 (Edge): The second edge
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

        # Calculates factors to use for interpolation with the edges and the step values to increase them by after drawing each span
        factor1 = float(e2.y1 - e1.y1) / e1ydiff
        factorStep1 = 1.0 / e1ydiff
        factor2 = 0.0
        factorStep2 = 1.0 / e2ydiff

        # Loops through the lines between the edges and draw spans
        for y in range(int(e2.y1), int(e2.y2)):
            # Creates and draw span
            span = Span(e1.color1 + (e1pointdiff * factor1), e1.x1 + int(e1xdiff * factor1), e2.color1 + (e2pointdiff * factor2), e2.x1 + int(e2xdiff * factor2))
            MaskImageCmdHelper.DrawSpan(bmp, span, y)

            # Increases factors
            factor1 += factorStep1
            factor2 += factorStep2

    @staticmethod
    def DrawTriangle(bmp, color1, x1, y1, color2, x2, y2, color3, x3, y3):
        """Draws a Triangle into the passed BaseBitmap.

        Args:
            bmp (c4d.bitmaps.BaseBitmap): The bitmap to draw in
            bmp (c4d.modules.bodypaint.PaintLayerBmp): The bitmap to draw in
            color1 (c4d.Vector): Color from (0,1) of the first point
            x1 (Union[float, int]): X position in uv space of the first point
            y1 (Union[float, int]): Y position in uv space of the first point
            color2 (c4d.Vector): Color from (0,1) of the second point
            x2 (Union[float, int]): X position in uv space of the second point
            y2 (Union[float, int]): Y position in uv space of the second point
            color3 (c4d.Vector): Color from (0,1) of the third point
            x3 (Union[float, int]): X position in uv space of the third point
            y3 (Union[float, int]): Y position in uv space of the third point
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
        MaskImageCmdHelper.DrawSpansBetweenEdges(bmp, edges[longEdge], edges[shortEdge1])
        MaskImageCmdHelper.DrawSpansBetweenEdges(bmp, edges[longEdge], edges[shortEdge2])

    @staticmethod
    def BakeMask(bmp, sculptObject):
        # Retrieves the current active layer from the sculpt object
        layer = sculptObject.GetCurrentLayer()
        if layer is None:
            raise RuntimeError("Failed to retrieve the selected layer for the sculpt object.")

        # Retrieves the polygon object representation of this sculpt object
        polyObject = sculptObject.GetPolygonCopy(sculptObject.GetCurrentLevel(), True)
        if polyObject is None:
            raise RuntimeError("Failed to retrieve the polygonal representation of the current sculpt object.")

        # Retrieves the first uvw tag on the polygon object
        uvs = polyObject.GetTag(c4d.Tuvw)
        if uvs is None:
            raise RuntimeError("Failed to retrieve uvw tag.")

        # Loops through all polygon to find if they are masked or not
        imageWidth = bmp.GetBw()
        imageHeight = bmp.GetBh()
        polyCount = polyObject.GetPolygonCount()
        for polyIndex in range(polyCount):
            status = float(polyIndex) / float(polyCount) * 100.0
            c4d.StatusSetBar(status)

            # Retrieves Cpolygon
            poly = polyObject.GetPolygon(polyIndex)

            # Retrieves UV information
            uvwdict = uvs.GetSlow(polyIndex)
            aX = uvwdict["a"].x * imageWidth
            aY = uvwdict["a"].y * imageHeight
            bX = uvwdict["b"].x * imageWidth
            bY = uvwdict["b"].y * imageHeight
            cX = uvwdict["c"].x * imageWidth
            cY = uvwdict["c"].y * imageHeight
            dX = uvwdict["d"].x * imageWidth
            dY = uvwdict["d"].y * imageHeight

            # Retrieves for each point if they are masked or not
            maskA = layer.GetMask(poly.a)
            maskB = layer.GetMask(poly.b)
            maskC = layer.GetMask(poly.c)
            maskD = layer.GetMask(poly.d)

            # Defines mask color
            colA = c4d.Vector(maskA)
            colB = c4d.Vector(maskB)
            colC = c4d.Vector(maskC)
            colD = c4d.Vector(maskD)

            # Draws them into the bitmap
            MaskImageCmdHelper.DrawTriangle(bmp, colA, aX, aY, colB, bX, bY, colC, cX, cY)
            if poly.c != poly.d:
                MaskImageCmdHelper.DrawTriangle(bmp, colA, aX, aY, colC, cX, cY, colD, dX, dY)

        c4d.StatusClear()


class MaskImageCmd(c4d.plugins.CommandData, MaskImageCmdHelper):

    def Execute(self, doc):
        """Called when the user Execute the command (CallCommand or a clicks on the Command from the plugin menu).

        Args:
            doc (c4d.documents.BaseDocument): the current active document

        Returns:
            True if the command success
        """
        # Retrieves the selected sculpt object
        sculptObject = c4d.modules.sculpting.GetSelectedSculptObject(doc)
        if sculptObject is None:
            raise RuntimeError("Failed to retrieve the selected sculpt object.")

        # Creates a BaseBitmap
        bmp = c4d.bitmaps.BaseBitmap()

        # Init the BaseBitmap
        if bmp.Init(1024, 1024, 32) != c4d.IMAGERESULT_OK:
            raise MemoryError("Failed to initialize the BaseBitmap.")

        # Bakes the mask of the sculpt object to the passed bitmap
        self.BakeMask(bmp, sculptObject)

        # Displays the bitmap into the Picture Viewer
        c4d.bitmaps.ShowBitmap(bmp)
        return True


if __name__ == "__main__":
    # Registers the command plugin
    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                      str="Python Sculpt Save Mask",
                                      info=0,
                                      help="Bake the sculpt mask to an image",
                                      dat=MaskImageCmd(),
                                      icon=None)
