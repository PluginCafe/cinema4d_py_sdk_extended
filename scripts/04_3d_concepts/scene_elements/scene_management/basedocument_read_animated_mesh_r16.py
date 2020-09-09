"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Animates a BaseDocument from frame 5 to 20.
    - Retrieves all the deformed mesh from the selected object.
    - Creates a Null for each frame at the position of point 88 of all deformed mesh.

Class/method highlighted:
    - BaseObject.GetDeformCache()
    - c4d.BaseTime()
    - BaseDocument.SetTime()
    - BaseDocument.ExecutePasses()

Compatible:
    - Win / Mac
    - R16, R17, R18, R19, R20, R21, S22, R23
"""
import c4d


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
        # If there is a cache iterates over its, a cache can also contain deformed cache
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


def main():
    # Saves current time
    ctime = doc.GetTime()

    # Retrieves BaseTime of frame 5, 20
    start = 5
    end = 20

    # Marks the state of the document as the initial step of our undo process
    doc.StartUndo()

    # Loops through the frames
    for frame in range(start, end + 1):
        # Changes the time of the document
        doc.SetTime(c4d.BaseTime(frame, doc.GetFps()))

        # Executes the document, so animation, dynamics, expression are calculated and cached are build accordingly
        buildflag = c4d.BUILDFLAGS_NONE if c4d.GetC4DVersion() > 20000 else c4d.BUILDFLAGS_0
        doc.ExecutePasses(None, True, True, True, buildflag)

        # For each cache objects of our current selected object
        for obj in DeformedPolygonCacheIterator(op):

            # Calculates the position of the point 88 in world space
            pos = obj.GetPoint(88) * obj.GetMg()

            # Creates a null for each frame and each cache
            null = c4d.BaseObject(c4d.Onull)
            null.SetName(str(frame))

            # Inserts the objects into the documents
            doc.AddUndo(c4d.UNDOTYPE_NEW, null)
            doc.InsertObject(null)

            # Defines the position of the null with the position of the point from the deformed mesh
            null.SetAbsPos(pos)

    # Sets the time back to the original time.
    doc.SetTime(ctime)

    # Executes the document, so animation, dynamics, expression are calculated and cached are build accordingly
    buildflag = c4d.BUILDFLAGS_NONE if c4d.GetC4DVersion() > 20000 else c4d.BUILDFLAGS_0
    doc.ExecutePasses(None, True, True, True, buildflag)

    # Marks the state of the document as the final step of our undo process
    doc.EndUndo()

    # Pushes an update event to Cinema 4D
    c4d.EventAdd(c4d.EVENT_ANIMATE)


if __name__ == "__main__":
    main()
