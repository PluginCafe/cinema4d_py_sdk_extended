"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Retrieves the color or each clone using two ways.
    - First one by accessing directly the Mograph Data.
    - Second one by accessing the polygon cache representation of the Mograph Cloner.

Class/method highlighted:
    - c4d.modules.mograph.GeGetMoData()
    - c4d.modules.mograph.MoData
    - MoData.GetArray()
    - BaseObject.GetCache()
    - BaseObject.GetDeformCache()

Compatible:
    - Win / Mac
    - R16, R17, R18, R19, R20, R21, S22
"""
import c4d


def RetrieveColorWithMoData(op):
    if not op.CheckType(1018544):
        raise TypeError("objects is not a cloner.")

    # Retrieves the modata
    md = c4d.modules.mograph.GeGetMoData(op)
    if md is None:
        return []

    # Retrieves the clone offset and the color array
    offset = op[c4d.MG_LINEAR_OFFSET]
    colorList = md.GetArray(c4d.MODATA_COLOR)

    # Appends the color list taking in account the offset (aka skip the first elements)
    return colorList[offset:]


def DeformedPolygonCacheIterator(op):
    """
    A Python Generator to iterate over all PolygonCache of passed BaseObject
    :param op: The BaseObject to retrieve all PolygonObject cache.
    """
    if not isinstance(op, c4d.BaseObject):
        raise TypeError("Expected a BaseObject or derived class got {0}".format(op.__class__.__name__))

    # Try to retrieve the deformed cache of the object
    temp = op.GetDeformCache()
    if temp is not None:
        # If there is a deformed cache we iterate over him, a deformed cache can also contain deformed cache
        # e.g. in case of a nested deformer
        for obj in DeformedPolygonCacheIterator(temp):
            yield obj

    # Try to retrieve the cache of the Object
    temp = op.GetCache()
    if temp is not None:
        # If there is a cache iterate over its, a cache can also contain deformed cache
        # e.g. an instance, have a cache of its linked object but if this object is deformed, then you have a deformed cache as well
        for obj in DeformedPolygonCacheIterator(temp):
            yield obj

    # If op is not a generator / modifier
    if not op.GetBit(c4d.BIT_CONTROLOBJECT):
        # If op is a PolygonObject we return it
        if op.IsInstanceOf(c4d.Opolygon):
            yield op

    # Then finally iterates over the child of the current object to retrieve all objects
    # e.g. in a cloner set to Instance mode, all clones is a new object.
    temp = op.GetDown()
    while temp:
        for obj in DeformedPolygonCacheIterator(temp):
            yield obj
        temp = temp.GetNext()


def RetrieveColorWithCache(op):
    # Iterates the polygon cache of a cloner (does work only, in case of simple instance mode)
    finalList = []
    # Iterates overs each polygon object cache
    for i, obj in enumerate(DeformedPolygonCacheIterator(op)):

        # Adds the object information in the list
        finalList.append(obj[c4d.ID_BASEOBJECT_COLOR])

    return finalList


def main():
    # Checks if there is a selected object, and this selected object get a child object.
    if not op:
        raise RuntimeError("Failed to retrieve op")

    # Checks if selected object and child objects are cloner objects.
    if not op.CheckType(1018544):
        raise TypeError("objects is not cloner.")

    print(RetrieveColorWithMoData(op))
    print(RetrieveColorWithCache(op))


if __name__ == "__main__":
    main()
