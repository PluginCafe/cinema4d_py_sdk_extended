"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Removes the polygon point selection to the uv points pinned.

Class/method highlighted:
    - c4d.UVWTag
    - UVWTag.RemoveFromPinSelection()
    - c4d.BaseSelect
    - c4d.modules.bodypaint.UpdateMeshUV()

Notes:
    UV Points are indexed by 4 * polygon + point where `c` polygon is the polygon index and `c` point is the point index between `0` and `3` (a, b, c, d).

"""
import c4d


def CPolygonGetItem(cPoly, idx):
    """Map 0-1-2-3 to the member a b c d of a c4d.CPolygon

    Args:
        cPoly: c4d.CPolygon
        idx: A polygon point index
    """
    # Checks if the cpolygon is a c4d.CPolygon
    if not isinstance(cPoly, c4d.CPolygon):
        raise TypeError("cPoly is not a c4d.CPolygon.")

    if not 0 <= idx <= 3:
        raise ValueError("{0} is not between 0 and 3 included.".format(idx))

    if idx == 0:
        return cPoly.a
    elif idx == 1:
        return cPoly.b
    elif idx == 2:
        return cPoly.c
    elif idx == 3:
        return cPoly.d
    raise RuntimeError("Unexpected Error.")


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Checks if the selected object is a PolygonObject
    if not isinstance(op, c4d.PolygonObject):
        raise TypeError("op is not a c4d.PolygonObject.")

    # Retrieves teh first UVW tag on the current object
    uvwTag = op.GetTag(c4d.Tuvw)
    if uvwTag is None:
        raise RuntimeError("Failed to retrieves a uvw tag on the object.")

    # Retrieves the current Point Selection stored in the PointObject
    ptSelect = op.GetPointS()
    if ptSelect is None:
        raise RuntimeError("Failed to retrieves the selected point.")

    # Retrieves all elements, selected or not, as booleans in a list
    rawSelectionList = ptSelect.GetAll(op.GetPointCount())

    # Retrieves the point ID that are selected from the rawSelectionList
    pointIdSelected = [i for i, value in enumerate(rawSelectionList) if value]

    # Gets all CPolygon of the selected object
    polyList = op.GetAllPolygons()

    # Creates a new pinSelection To Set
    pinsToSet = c4d.BaseSelect()

    # For each CPolygon convert point selection to uv point id
    for polyId in range(op.GetPolygonCount()):
        # Get the CPolygon
        cPoly = polyList[polyId]

        # Iterate over each Point of a CPolygon (4 points), a, b ,c and d
        for polyPtId in range(4):
            # Selects the uv point pinned if PointId of the CPolygon is selected
            ptId = CPolygonGetItem(cPoly, polyPtId)
            if ptId in pointIdSelected:
                pinsToSet.Select(polyId * 4 + polyPtId)

    # Adds the built selection to the current pin selection
    uvwTag.RemoveFromPinSelection(pinsToSet)

    # Refresh the UV view
    c4d.modules.bodypaint.UpdateMeshUV(False)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
