"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Calls BodyPaint 3D UV commands.

Class/method highlighted:
    - c4d.modules.bodypaint.GetActiveUVSet()
    - c4d.modules.bodypaint.CallUVCommand()

"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Enables UV Polygon Mode if not already in any UV mode (needed for GetActiveUVSet to works)
    if doc.GetMode() not in [c4d.Muvpoints, c4d.Muvpolygons]:
        doc.SetMode(c4d.Muvpolygons)

    # Retrieves active UVSet, The UV windows need to be opened at least one time
    handle = c4d.modules.bodypaint.GetActiveUVSet(doc, c4d.GETACTIVEUVSET_ALL)
    if handle is None:
        # If fail it may be because the Texture view is not open
        # Open A texture View
        c4d.CallCommand(170103)
        # In S22 you need to update the UV Mesh
        if c4d.API_VERSION >= 22000:
            c4d.modules.bodypaint.UpdateMeshUV(False)

        # Retrieves active UVSet, The UV windows need to be opened at least one time
        handle = c4d.modules.bodypaint.GetActiveUVSet(doc, c4d.GETACTIVEUVSET_ALL)
        if handle is None:
            raise RuntimeError("There is no Active UVSet")

    # Prints UVSet information
    print("UV Handle Data:")
    print("Handle: {0}".format(handle))
    print("Handle Mode: {0}".format(handle.GetMode()))
    print("Handle Points: {0}".format(handle.GetPoints()))
    print("Handle Polygons: {0}".format(handle.GetPolys()))
    print("Handle Polygon Selection: {0}".format(handle.GetPolySel()))
    print("Handle Hidden Polygons: {0}".format(handle.GetPolyHid()))
    print("Handle Point Selection: {0}".format(handle.GetUVPointSel()))
    print("Handle Point Count: {0}".format(handle.GetPointCount()))
    print("Handle Polygon Count: {0}".format(handle.GetPolyCount()))
    print("Handle Object: {0}".format(handle.GetBaseObject()))
    print("Handle Editable: {0}".format(handle.IsEditable()))
    print("Handle UVW: {0}".format(handle.GetUVW()))

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
        raise RuntimeError("UVW from Texture View failed to be set.")

    print("UVW from Texture View successfully set")

    # Releases active UVSet
    c4d.modules.bodypaint.FreeActiveUVSet(handle)


if __name__ == '__main__':
    main()
