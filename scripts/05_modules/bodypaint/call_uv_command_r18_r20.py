"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Calls BodyPaint 3D UV commands.

Class/method highlighted:
    - c4d.modules.bodypaint.GetActiveUVSet()
    - c4d.modules.bodypaint.CallUVCommand()

Compatible:
    - Win / Mac
    - R18, R19, R20
"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Retrieves active UVSet, The UV windows need to be opened at least one time.
    handle = c4d.modules.bodypaint.GetActiveUVSet(doc, c4d.GETACTIVEUVSET_ALL)
    if handle is None:
        raise RuntimeError("There is no Active UVSet, lease open at least one time the Texture View.")

    # Prints UVSet information
    print "UV Handle Data:"
    print "Handle:", handle
    print "Handle Mode:", handle.GetMode()
    print "Handle Points:", handle.GetPoints()
    print "Handle Polygons:", handle.GetPolys()
    print "Handle Polygon Selection:", handle.GetPolySel()
    print "Handle Hidden Polygons:", handle.GetPolyHid()
    print "Handle Point Selection:", handle.GetUVPointSel()
    print "Handle Point Count:", handle.GetPointCount()
    print "Handle Polygon Count:", handle.GetPolyCount()
    print "Handle Object:", handle.GetBaseObject()
    print "Handle Editable:", handle.IsEditable()
    print "Handle UVW:", handle.GetUVW()

    # Builds UVCOMMAND_TRANSFORM container for the command settings
    settings = c4d.BaseContainer()
    settings[c4d.UVCOMMAND_TRANSFORM_MOVE_X] = 0
    settings[c4d.UVCOMMAND_TRANSFORM_MOVE_Y] = 0
    settings[c4d.UVCOMMAND_TRANSFORM_SCALE_X] = 1
    settings[c4d.UVCOMMAND_TRANSFORM_SCALE_Y] = 1
    settings[c4d.UVCOMMAND_TRANSFORM_ANGLE] = c4d.utils.DegToRad(90)

    # Retrieves UVW list
    uvw = handle.GetUVW()
    if uvw is None:
        raise RuntimeError("Failed to retrieve the uvw from the the texture view.")

    # Calls UVCOMMAND_TRANSFORM to change UVW list
    ret = c4d.modules.bodypaint.CallUVCommand(handle.GetPoints(),
                                              handle.GetPointCount(),
                                              handle.GetPolys(),
                                              handle.GetPolyCount(),
                                              uvw,
                                              handle.GetPolySel(),
                                              handle.GetUVPointSel(),
                                              op,
                                              handle.GetMode(),
                                              c4d.UVCOMMAND_TRANSFORM,
                                              settings)
    if not ret:
        raise RuntimeError("CallUVCommand failed.")

    # Sets the transformedUVW from Texture View 
    if not handle.SetUVWFromTextureView(uvw, True, True, True):
        raise  RuntimeError("UVW from Texture View failed to be set.")

    print "UVW from Texture View successfully set"

    # Releases active UVSet
    c4d.modules.bodypaint.FreeActiveUVSet(handle)


if __name__ == '__main__':
    main()
