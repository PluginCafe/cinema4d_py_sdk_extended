"""
Copyright: MAXON Computer GmbH
Author: Kent Barber

Description:
    - Brush Tool, modifying a BaseObject by grabbing all points under the brush.

Class/method highlighted:
    - c4d.plugins.SculptBrushToolData
    - SculptBrushToolData.GetToolPluginId()
    - SculptBrushToolData.GetResourceSymbol()
    - SculptBrushToolData.PostInitDefaultSettings()
    - SculptBrushToolData.ApplyDab()

"""
import c4d

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1031347

# Values must match with the header file
IDS_PYTHON_BRUSH_GRAB = 10000


class SculptBrushGrabTool(c4d.plugins.SculptBrushToolData):
    """Inherit from SculptBrushToolData to create your own sculpting tool"""

    def GetToolPluginId(self):
        """Called by Cinema 4D, to know the plugin ID of this tool.

        Returns:
            int: The unique id for the tool plugin as obtained from www.plugincafe.com
        """
        return PLUGIN_ID

    def GetResourceSymbol(self):
        """Called by Cinema 4D, to know the resource to be used for this tool.

        Returns:
            str: The resource name of the tool
        """
        return "pythongrabbrush"

    def PostInitDefaultSettings(self, doc, data):
        """Called by Cinema 4D, to define custom default values.

        See the pythongrabbrush.res and pythongrabbrush.h files for where this value is defined.

        Args:
            doc (c4d.documents.BaseDocument): The current document.
            data (c4d.BaseContainer): The settings for the loaded brush.
        """
        data.SetInt32(c4d.MDATA_PYTHONGRABBRUSH_DIRMODE, c4d.MDATA_PYTHONGRABBRUSH_DIRMODE_MOUSEDIR)

    def ApplyDab(self, dab):
        """Called by Cinema 4D to modify the sculpt object.

        Implement the brush functionality in this method.

        Args:
            dab (c4d.modules.sculpting.BrushDabData): The brush dab data.
        """
        # Retrieves the Polygon Object
        polyObj = dab.GetPolygonObject()
        if polyObj is None:
            return False

        # Retrieves the world matrix for the model
        mat = polyObj.GetMg()

        # Retrieves the location of the hit point on the model in world coordinates
        hitPointWorld = mat * dab.GetHitPoint()

        # Zero out the offset since its no longer required
        mat.off = c4d.Vector(0, 0, 0)

        # Retrieves the settings of the brush
        data = dab.GetData()

        # Retrieves the custom direction parameter value
        dirMode = data.GetInt32(c4d.MDATA_PYTHONGRABBRUSH_DIRMODE)

        # Calculates the distance from the mouse has moved in world coordinates by getting the world position of the mouse and subtracting the current grab brush world coordinate
        moveAmnt = dab.GetMousePos3D() - hitPointWorld

        # Transforms this distance into a vector that is in the local coordinates of the model.
        invertMat = mat.__invert__()
        moveAmnt = invertMat * moveAmnt

        # If direction mode is set to normal
        if dirMode == c4d.MDATA_PYTHONGRABBRUSH_DIRMODE_NORMAL:
            # Retrieves the current normal
            normal = dab.GetNormal()

            # Retrieves the length of the distance vector to scale the normal.
            moveAmnt = normal * moveAmnt.GetLength()

            # Adjusts the direction of the vector depending on if its moving above the surface or below it.
            dot = normal.Dot(moveAmnt)
            if dot < 0:
                moveAmnt *= -1

        # Retrieves the number of points affected by the brush
        pointCount = dab.GetPointCount()

        # Checks if symmetry is enabled
        mirror = dab.IsMirroredDab()

        # Loops over every point on the dab and move them by the moveAmnt.
        for pointIdDab in range(pointCount):
            # Retrieves the index of the point on the PolygonObject.
            pointData = dab.GetPointData(pointIdDab)
            pointIndex = pointData["pointIndex"]

            # Retrieves the falloff value for this point. This value will take into account the current stencil, stamp settings and the falloff curve to create this value.
            fallOff = dab.GetBrushFalloff(pointIdDab)

            # Retrieves the original points on the surface of the object. These points are the state of the object when the
            # user first clicks on the model to do a mouse stroke. This allows you to compare where the points are during
            # a stroke, since you have moved them, when the original positions.
            original = dab.GetOriginalPoint(pointIndex)

            # Retrieves the vector of the point we are going to change.
            currentPoint = dab.GetPoint(pointIndex)

            # If the user has any of the symmetry settings enabled and this is one of the symmetrical brush instance then mirror will be True.
            # We can check to see if another brush instance has already touched this point and moved it by calling the IsPointModified method.
            # If a point has been touched then that means it has already been moved by a certain vector by that brush instance.
            # So we just offset it by another vector and do not worry about the original location of the point.
            if mirror and dab.IsPointModified(pointIndex):
                # Adjust the offset by the new amount.
                dab.OffsetPoint(pointIndex, moveAmnt * fallOff)
            else:
                # If there is no symmetry or the point hasn't been touched then we can just set the position of the point normally.
                # First determine the offset vector by using the original location of the point and adding on the new point after it has been adjusted by the falloff value.
                newPosOffset = original + moveAmnt * fallOff

                # A new offset is calculated by using this new point and its current position.
                offset = newPosOffset - currentPoint

                # Offset the point to place it in the correct location.
                dab.OffsetPoint(pointIndex, offset)

        # Ensure that all the points for the dab are marked as dirty. This is required to ensure that they all update even if they were not directly
        # touched by this brush instance. Marking all points as dirty ensures that the normals for all points are updated. This is only required
        # for grab brushes when multiple brush instances are touching the same points.
        dab.DirtyAllPoints(c4d.SCULPTBRUSHDATATYPE_POINT)
        return True


if __name__ == "__main__":
    # Defines global parameter for the brush (how the brush should act)
    params = c4d.modules.sculpting.SculptBrushParams()
    params.SetBrushMode(c4d.SCULPTBRUSHMODE_GRAB)
    params.SetUndoType(c4d.SCULPTBRUSHDATATYPE_POINT)

    # Registers the tool brush plugins
    c4d.plugins.RegisterSculptBrushPlugin(id=PLUGIN_ID,
                                          str="Python Grab Brush",
                                          info=0, icon=None,
                                          help="Python Grab Brush",
                                          sculptparams=params,
                                          dat=SculptBrushGrabTool())
