"""
Copyright: MAXON Computer GmbH
Author: Kent Barber

Description:
    - Brush Tool, modifying a BaseObject by twisting all points under the brush.

Class/method highlighted:
    - c4d.plugins.SculptBrushToolData
    - SculptBrushToolData.GetToolPluginId()
    - SculptBrushToolData.GetResourceSymbol()
    - SculptBrushToolData.OverwriteLoadedPresetSettings()
    - SculptBrushToolData.ApplyDab()

Compatible:
    - Win / Mac
    - R16, R17, R18, R19, R20, R21
"""
import c4d

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1031350

# Values must match with the header file
IDS_PYTHON_BRUSH_TWIST = 10000


class SculptBrushTwistTool(c4d.plugins.SculptBrushToolData):
    """ Inherit from SculptBrushToolData to create your own sculpting tool """

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
        return "pythontwistbrush"

    def OverwriteLoadedPresetSettings(self, data):
        """
        Called by Cinema 4D, after a preset has been loaded.
        :param data: The settings for the loaded brush.
        :type data: c4d.BaseContainer()
        """
        data[c4d.MDATA_SCULPTBRUSH_STAMP_FOLLOW] = False

    def ApplyDab(self, dab):
        """
        Called by Cinema 4D, to modify the sculpt object.
        Implement the brush functionality in this method
        :param dab: The brush dab data.
        :type dab: c4d.modules.sculpting.BrushDabData
        """
        # Retrieves the Polygon Object
        poly = dab.GetPolygonObject()
        if poly is None:
            return False

        # Retrieves the world matrix for the model
        mat = poly.GetMg()

        # Retrieves the location of the hit point on the model in world coordinates
        hitPointWorld = mat * dab.GetHitPoint()

        # Predict movement amplitude
        twistGrabMoveAmnt = (dab.GetMousePos3D() - hitPointWorld)
        mat.off = c4d.Vector(0,0,0)
        twistGrabMoveAmnt = ~mat * twistGrabMoveAmnt

        # TwistGrab along the normal
        normal = dab.GetNormal()
        dot = normal.Dot(twistGrabMoveAmnt)
        twistGrabMoveAmnt = normal * twistGrabMoveAmnt.GetLength()
        if dot < 0:
            twistGrabMoveAmnt *= -1

        # Retrieves the averages points position and normal
        pointAndNormal = dab.GetAveragePointAndNormal()

        # Calculates the rotation, by looking at the mouse movement, since now and initial position
        hitScreenSpace = dab.GetBaseDraw().WS(hitPointWorld)
        currentDrawLocation = dab.GetBaseDraw().WS(dab.GetMousePos3D())
        xVal = currentDrawLocation.x - hitScreenSpace.x
        rotation = c4d.utils.Rad(xVal)

        # Loops over very point for this dab and move it if we need to.
        pointCount = dab.GetPointCount()
        mirrored = dab.IsMirroredDab()
        for a in xrange(0,pointCount):
            # Retrieves the index of the point on the PolygonObject.
            pointData = dab.GetPointData(a)
            pointIndex = pointData["pointIndex"]

            #Retrieves the falloff for this point. This will always be a value from 0 to 1.
            # The value returned is a combination of the following values all multiplied together to give a final value.
            # - The falloff curve.
            # - The color of the stamp with its color value averaged to gray and adjusted by the Gray Value.
            # - The color of the stencil with its color value averaged to gray and adjusted by the Gray Value.
            fallOff = dab.GetBrushFalloff(a)

            # If the falloff value is 0 then we don't have to do anything at all.
            if fallOff == 0:
                continue

            # Retrieves the original points on the surface of the object. These points are the state of the object when the
            # user first clicks on the model to do a mouse stroke. This allows you to compare where the points are during
            # a stroke, since you have moved them, when the original positions.
            original = dab.GetOriginalPoint(pointIndex)

            # Retrieves the vector of the point we are going to change.
            currentPoint = dab.GetPoint(pointIndex)

            rotationMatrix = c4d.utils.RotAxisToMatrix(pointAndNormal["normal"], rotation * fallOff)

            # If the point has been touched and we are in mirror mode then do something special
            if mirrored and dab.IsPointModified(pointIndex):
                newPosition = currentPoint - hitPointWorld
                newPosition = rotationMatrix * newPosition
                newPosition += hitPointWorld
                newOffset = newPosition - currentPoint
                dab.OffsetPoint(pointIndex, newOffset)
            else:
                newPosition = original - hitPointWorld
                newPosition = rotationMatrix * newPosition
                newPosition += hitPointWorld
                offset = newPosition - currentPoint
                dab.OffsetPoint(pointIndex, offset)

        # Notifies that point were changed
        dab.DirtyAllPoints(c4d.SCULPTBRUSHDATATYPE_POINT)
        return True


if __name__ == "__main__":
    # Defines global parameter for the brush (how the brush should act)
    params = c4d.modules.sculpting.SculptBrushParams()
    params.EnableStencil(False)
    params.EnableStamp(False)
    params.SetBrushMode(c4d.SCULPTBRUSHMODE_GRAB)
    params.SetUndoType(c4d.SCULPTBRUSHDATATYPE_POINT)

    # Registers the tool brush plugins
    c4d.plugins.RegisterSculptBrushPlugin(id=PLUGIN_ID,
                                          str="Python Twist Brush",
                                          info=0, icon=None,
                                          help="Python Twist Brush",
                                          sculptparams=params,
                                          dat=SculptBrushTwistTool())
