"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Copies the UV seams to the edge polygon selection.

Class/method highlighted:
    - c4d.modules.bodypaint.GetUVSeams()
    - PolygonObject.GetEdgeS()
    - BaseSelect.CopyTo()
    - c4d.modules.bodypaint.UpdateMeshUV()

"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Checks if there is a texture tag selected
    if doc.GetActiveTag() is None or not doc.GetActiveTag().CheckType(c4d.Tuvw) or doc.GetActiveTag().GetObject() != op:
        raise RuntimeError("A UVW tag being part of the select op should be selected.")

    # Enables UV Edge Mode if not already in any UV mode (needed for GetActiveUVSet to works)
    docMode = doc.GetMode()
    if docMode not in [c4d.Muvpoints, c4d.Muvedges, c4d.Muvpolygons]:
        doc.SetMode(c4d.Muvpolygons)

    # UVSet have to be defined to do that ensure the UV windows is opened at least one time
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

    uvSeams = c4d.modules.bodypaint.GetUVSeams(op)
    if uvSeams is None:
        raise RuntimeError("Failed to retrieves the uv seams.")

    if uvSeams.GetCount() == 0:
        raise RuntimeError("There is no seams for the selected object.")

    # Retrieves the current Edge Selection stored in the Polygon Object
    edgeSelect = op.GetEdgeS()
    if edgeSelect is None:
        raise RuntimeError("Failed to retrieves the edge selection.")

    # Deselect all the currently selected edge
    edgeSelect.DeselectAll()

    # Copies the UV seams to the Polygon Edge selection.
    uvSeams.CopyTo(edgeSelect)

    # Resets the previous document mode
    doc.SetMode(docMode)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
