"""
Copyright: MAXON Computer GmbH
Author: Kent Barber

Description:
    - Brush Tool, modifying a BaseObject by pulling all points under the brush.

Class/method highlighted:
    - c4d.plugins.SculptBrushToolData
    - SculptBrushToolData.GetToolPluginId()
    - SculptBrushToolData.GetResourceSymbol()
    - SculptBrushToolData.PostInitDefaultSettings()
    - SculptBrushToolData.ApplyDab()

Compatible:
    - Win / Mac
    - R16, R17, R18, R19, R20, R21
"""
import c4d


# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1031349

# Values must match with the header file
IDS_PYTHON_BRUSH_PULL = 10000


class SculptBrushPullTool(c4d.plugins.SculptBrushToolData):
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
        return "pythonpullbrush"

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

        # Retrieves tool parameters
        bc = dab.GetData()

        # Retrieves polygons count affected
        pointCount = dab.GetPointCount()

        # Retrieves if it's a preview action (aka do nothing on the mesh)
        usePreview = dab.IsPreviewDab()

        # Retrieves polygons objects affected
        polyObj = dab.GetPolygonObject()

        # Retrieves the radius (size) of the object bounding box
        rad = polyObj.GetRad()

        # Pre-calculates the offset vector
        dim = rad.GetLength() * 0.005
        buildup = bc.GetFloat(c4d.MDATA_SCULPTBRUSH_SETTINGS_BUILDUP) * 0.002
        pressurePreMult = strength * 10.0 * buildup * dim
        multPreMult = dab.GetNormal() * pressurePreMult

        # Checks if the user hold the CLTR key (it will sets OVERRIDE_INVERT)
        invert = dab.GetBrushOverride() & c4d.OVERRIDE_INVERT
        if invert is True or bc.GetBool(c4d.MDATA_SCULPTBRUSH_SETTINGS_INVERT) is True:
            # Inverses the direction according result
            multPreMult = -multPreMult

        # Checks if the invert checkbox is enabled in the UI.
        if bc.GetBool(c4d.MDATA_SCULPTBRUSH_SETTINGS_INVERT) is True:
            # Inverses the direction according result
            multPreMult = -multPreMult

        # Loops over every points for this dab and move it if we need to.
        for a in xrange(0, pointCount):
            # Retrieves the index of the point on the PolygonObject.
            pointData = dab.GetPointData(a)
            pointIndex = pointData["pointIndex"]

            # Retrieves the falloff for this point. This will always be a value from 0 to 1.
            # The value returned is a combination of the following values all multiplied together to give a final value.
            # - The falloff curve.
            # - The color of the stamp with its color value averaged to gray and adjusted by the Gray Value.
            # - The color of the stencil with its color value averaged to gray and adjusted by the Gray Value.
            fallOff = dab.GetBrushFalloff(a)

            # If the falloff value is 0 then we don't have to do anything at all.
            if fallOff == 0:
                continue

            # Multiplies the falloff value with the multiply vector we calculated early. This will result in an offset vector that we want to move the vertex on the model by.
            res = fallOff * multPreMult

            # If the brush is not in preview mode (preview mode happens with in DragDab or DragRect mode) then we can offset the final point on the selected layer.
            if usePreview is False:
                dab.OffsetPoint(pointIndex, res)
            # Otherwise applies the offset to the preview layer.
            else:
                dab.OffsetPreviewPoint(pointIndex, res)
        return True


if __name__ == "__main__":
    # Defines global parameter for the brush (how the brush should act)
    params = c4d.modules.sculpting.SculptBrushParams()
    params.EnableInvertCheckbox(True)
    params.EnableBuildup(True)
    params.EnableModifier(True)
    params.SetFloodType(c4d.SCULPTBRUSHDATATYPE_POINT)
    params.SetBrushMode(c4d.SCULPTBRUSHMODE_NORMAL)
    params.SetFirstHitPointType(c4d.FIRSTHITPPOINTTYPE_SELECTED)
    params.SetUndoType(c4d.SCULPTBRUSHDATATYPE_POINT)

    # Registers the tool brush plugins
    c4d.plugins.RegisterSculptBrushPlugin(id=PLUGIN_ID,
                                          str="Python Pull Brush",
                                          info=0, icon=None,
                                          help="Python Pull Brush",
                                          sculptparams=params,
                                          dat=SculptBrushPullTool())
