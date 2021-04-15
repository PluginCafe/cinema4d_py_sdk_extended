"""
Copyright: MAXON Computer GmbH
Author: Riccardo Gigante, Maxime Adam

Description:
    - Retrieves the first child object and offset all its points on the y-axis by a specific value. Tangents are unaffected.
    - Demonstrates a Spline Generator that requires Input Spline and Outputs a valid Spline everywhere in Cinema 4D.

Note:
    - SplineInputGeneratorHelper is a class holding utility functions
        SplineInputGeneratorHelper.OffsetSpline is the function responsible for moving points.

Class/method highlighted:
    - c4d.SplineObject / c4d.LineObject / c4d.PointObject
    - c4d.plugins.ObjectData
    - ObjectData.Init()
    - ObjectData.GetDimension()
    - ObjectData.CheckDirty()
    - ObjectData.GetVirtualObjects()
    - ObjectData.GetContour()

"""
import c4d

PLUGIN_ID = 98989801


class SplineInputGeneratorHelper(object):

    @staticmethod
    def FinalSpline(sourceSplineObj):
        """Retrieves the final (deformed) representation of the spline.

        Args:
            sourceSplineObj (c4d.BaseObject or c4d.SplineObject or LineObject): A c4d.BaseObject that can be represented as a Spline.

        Returns:
            c4d.SplineObject: The final Spline/Line Object, SplineObject should be returned when it's possible
        """
        if sourceSplineObj is None:
            raise TypeError("Expect a spline object got {0}".format(sourceSplineObj.__class__.__name__))

        if sourceSplineObj.IsInstanceOf(c4d.Onull):
            return None

        # Checks if sourceSplineObj can be treated as a spline
        if not sourceSplineObj.IsInstanceOf(c4d.Oline) and not sourceSplineObj.GetInfo() & c4d.OBJECT_ISSPLINE:
            raise TypeError("Expect an object that can be treated as spline object.")

        # If there is a Deformed cache, retrieves it, but it seems it's never the case
        deformedCache = sourceSplineObj.GetDeformCache()
        if deformedCache is not None:
            sourceSplineObj = deformedCache

        # Returns the LineObject if it's a LineObject
        if sourceSplineObj.IsInstanceOf(c4d.Oline):
            return sourceSplineObj

        # Retrieves the SplineObject
        realSpline = sourceSplineObj.GetRealSpline()
        if realSpline is None:
            raise RuntimeError("Failed to retrieve the real c4d.SplineObject from {0}".format(sourceSplineObj))

        return realSpline

    @staticmethod
    def OffsetSpline(inputSpline, offsetValue):
        """Performs the Y-Offset of the spline. 

        Take care the inputSpline can be sometime a LineObject or a SplineObject depending of the context (called from GVO or GetContour).

        Args:
            inputSpline (Union[c4d.LineObject, c4d.SplineObject]): The original LineObject or SplineObject
            offsetValue (float): The amount to offset Y parameter

        Returns:
            Union[c4d.LineObject, c4d.SplineObject]: A new Line/Spline instance
        """
        if inputSpline is None:
            raise TypeError("Expect a SplineObject got {0}".format(inputSpline.__class__.__name__))

        # Checks if the the input object is a SplineObject or a LineObject
        if not inputSpline.IsInstanceOf(c4d.Ospline) and not inputSpline.IsInstanceOf(c4d.Oline):
            raise TypeError("Expect a SplineObject or a LineObject got {0}".format(inputSpline.__class__.__name__))

        # Retrieves a clones of the Splines/LineObject, so tangents and all parameters are kept.
        resSpline = inputSpline.GetClone()
        if resSpline is None:
            raise MemoryError("Failed to create a new Spline Object.")

        # Retrieves all points position of the source object
        allPts = inputSpline.GetAllPoints()
        if not allPts:
            return

        # Adds the offsetValue in Y for each point (this is done only in memory)
        allPtsOffsets = [c4d.Vector(pt.x, pt.y + offsetValue, pt.z) for pt in allPts]

        # Sets all points of the resSpline from the list previously calculated.
        resSpline.SetAllPoints(allPtsOffsets)

        # Notifies about the generator update
        resSpline.Message(c4d.MSG_UPDATE)

        # Returns the computed spline
        return resSpline

    @staticmethod
    def GetCloneSpline(op):
        """Emulates the GetHierarchyClone in the GetContour by using the SendModelingCommand.

        Args:
            op (c4d.BaseObject): The Object to clone and retrieve the current state (take care the whole hierarchy is join into one object.

        Returns:
            Union[c4d.BaseObject, None]: The merged object or None, if the retrieved object is not a Spline.
        """
        # Copies the original object
        childSpline = op.GetClone(c4d.COPYFLAGS_NO_ANIMATION)
        if childSpline is None:
            raise RuntimeError("Failed to copy the child spline.")

        doc = c4d.documents.BaseDocument()
        if not doc:
            raise RuntimeError("Failed to Create a Doc")

        doc.InsertObject(childSpline)

        # Performs a Current State to Object
        resultCSTO = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_CURRENTSTATETOOBJECT, list=[childSpline], doc=doc)
        if not isinstance(resultCSTO, list) or not resultCSTO:
            raise RuntimeError("Failed to perform MCOMMAND_CURRENTSTATETOOBJECT.")

        childSpline = resultCSTO[0]

        # If the results is a Null, performs a Join command to retrieve only one object.
        if childSpline.CheckType(c4d.Onull):
            resultJoin = c4d.utils.SendModelingCommand(command=c4d.MCOMMAND_JOIN, list=[childSpline], doc=doc)
            if not isinstance(resultJoin, list) or not resultJoin:
                raise RuntimeError("Failed to perform MCOMMAND_JOIN.")

            childSpline = resultJoin[0]

        if childSpline is None:
            raise RuntimeError("Failed to retrieve cached spline.")

        # Checks if childSpline can be interpreted as a Spline.
        if not childSpline.GetInfo() & c4d.OBJECT_ISSPLINE and not childSpline.IsInstanceOf(c4d.Ospline) and not childSpline.IsInstanceOf(c4d.Oline):
            return None

        return childSpline

    @staticmethod
    def HierarchyIterator(obj):
        """A Generator to iterate over the Hierarchy.

        Args:
            obj (c4d.BaseObject): The starting object of the generator (will be the first result)

        Returns:
            c4d.BaseObject: All objects under and next of the `obj`
        """
        while obj:
            yield obj
            for opChild in SplineInputGeneratorHelper.HierarchyIterator(obj.GetDown()):
                yield opChild
            obj = obj.GetNext()


class OffsetYSpline(c4d.plugins.ObjectData):

    _childContourDirty = 0  # type: int
    _childGVODirty = -1  # type: int

    def Init(self, op):
        if op is None:
            raise RuntimeError("Failed to retrieve op.")

        self.InitAttr(op, float, [c4d.PY_OFFSETYSPLINE_OFFSET])
        op[c4d.PY_OFFSETYSPLINE_OFFSET] = 100.0

        # Defines members variable to store the dirty state of Children Spline
        self._childContourDirty = 0
        self._childGVODirty = -1

        return True

    def GetDimension(self, op, mp, rad):
        """This Method is called automatically when Cinema 4D try to retrieve the boundaries of the object.

        Args:
            op (c4d.BaseObject): The Python Generator base object.
            mp (c4d.Vector): Assign the center point of the bounding box to this vector.
            rad (float): Assign the XYZ bounding box radius to this vector.
        """
        if op is None:
            raise RuntimeError("Failed to retrieve op.")

        # Initializes default values
        mp, rad = c4d.Vector(), c4d.Vector()

        # If there is no child, that means the generator output nothing, so an empty size
        if op.GetDown() is None:
            return

        # Assigns value as the child object
        rad = op.GetDown().GetRad()
        mp = op.GetMg().off

        # Offsets the bounding box by the Y offset the generator deliver
        mp.y = op.GetMg().off.y + op[c4d.PY_OFFSETYSPLINE_OFFSET]

    def CheckDirty(self, op, doc):
        """This Method is called automatically when Cinema 4D ask the object is dirty,
        something changed so a new computation of the generator is needed.

        In reality this is only useful for GetContour, GetVirtualObjects is automatically handled by Cinema 4D,
        But since the spline returned by GetContour is cached by Cinema 4D, you have to use CheckDirty
        To define when a new call of GetContour is needed. Moreover CheckDirty is only called in some special event,
        e.g. the Python Spline Generator is under another Python Spline generator.

        Args:
            op (c4d.BaseObject): The Python Generator c4d.BaseObject.
            doc (c4d.documents.BaseDocument): The document containing the plugin object.
        """
        if op is None or doc is None:
            raise RuntimeError("Failed to retrieve op or doc.")

        # Retrieves the First Child
        child = op.GetDown()
        if child is None:
            self._childContourDirty = -1
            op.SetDirty(c4d.DIRTYFLAGS_DATA)
            return

        # Retrieves the dirty count of the first child if there is a spline, otherwise set it to -1
        childDirty = child.GetDirty(c4d.DIRTYFLAGS_DATA | c4d.DIRTYFLAGS_MATRIX | c4d.DIRTYFLAGS_CACHE)

        # Checks if the dirty changed, if this is the case set op as dirty (it will force GetContour to be called)
        if childDirty != self._childContourDirty:
            self._childContourDirty = childDirty
            op.SetDirty(c4d.DIRTYFLAGS_DATA)

    def GetVirtualObjects(self, op, hh):
        """This method is called automatically when Cinema 4D ask for the cache of an object. 

        This is also the place where objects have to be marked as input object by touching them (destroy their cache in order to disable them in Viewport)

        Args:
            op (c4d.BaseObject): The Python Generator c4d.BaseObject.
            hh (c4d.HierarchyHelp): The helper object.

        Returns:
            Union[c4d.LineObject, c4d.SplineObject]: The represented Spline.
        """
        if op is None or hh is None:
            raise RuntimeError("Failed to retrieve op or hh.")

        # Retrieves the first enabled child
        child = op.GetDown()
        if child is None:
            self._childGVODirty = -1
            return

        # Touches all others children sine we don't want to have them later
        for obj in SplineInputGeneratorHelper.HierarchyIterator(op.GetDown().GetNext()):
            obj.Touch()

        # Retrieves the Clones, then mark them as read
        resGHC = op.GetHierarchyClone(hh, child, c4d.HIERARCHYCLONEFLAGS_ASSPLINE)
        if resGHC is None:
            resGHC = op.GetAndCheckHierarchyClone(hh, child, c4d.HIERARCHYCLONEFLAGS_ASSPLINE, False)
        if resGHC is None:
            return None

        # Retrieves results
        opDirty = resGHC["dirty"]
        childSpline = resGHC["clone"]
        if childSpline is None:
            return None

        # Checks if childSpline can be interpreted as a Spline.
        if not childSpline.GetInfo() & c4d.OBJECT_ISSPLINE and not childSpline.IsInstanceOf(c4d.Ospline) and not childSpline.IsInstanceOf(c4d.Oline):
            return None

        # Checks if the dirty of the child changed
        opDirty |= op.IsDirty(c4d.DIRTYFLAGS_DATA | c4d.DIRTYFLAGS_MATRIX)
        childDirty = child.GetDirty(c4d.DIRTYFLAGS_DATA | c4d.DIRTYFLAGS_MATRIX | c4d.DIRTYFLAGS_CACHE)

        # If the dirty count didn't change, return the cache
        if childDirty == self._childGVODirty and not opDirty:
            self._childGVODirty = child.GetDirty(c4d.DIRTYFLAGS_DATA | c4d.DIRTYFLAGS_MATRIX | c4d.DIRTYFLAGS_CACHE)
            return op.GetCache()

        # Retrieves the deformed Spline/LineObject (most of the time it's a LineObject)
        deformedSpline = SplineInputGeneratorHelper.FinalSpline(childSpline)
        if deformedSpline is None:
            return c4d.BaseObject(c4d.Onull)

        # Performs operation on the spline
        resSpline = SplineInputGeneratorHelper.OffsetSpline(deformedSpline, op[c4d.PY_OFFSETYSPLINE_OFFSET])

        # Returns the modified spline
        return resSpline

    def GetContour(self, op, doc, lod, bt):
        """This method is called automatically when Cinema 4D ask for a SplineObject, it's not called every time,
        only in some conditions like nested Spline Generator.

        Args:
            op (c4d.BaseObject): The Python Generator c4d.BaseObject.
            doc (c4d.documents.BaseDocument): The document containing the plugin object.
            lod (int): The level of detail.
            bt (c4d.threading.BaseThread): The executing thread.

        Returns:
            The SplineObject representing the final Spline.
        """
        if op is None or doc is None:
            raise RuntimeError("Failed to retrieve op or doc.")

        # Retrieves the first spline and set dirtyCount to 0 if the spline does not exists.
        childSpline = op.GetDown()
        if childSpline is None:
            self._childContourDirty = 0
            return None

        # Retrieves a Clone working spline.
        childSplineClone = SplineInputGeneratorHelper.GetCloneSpline(childSpline)
        if childSplineClone is None:
            return None

        # Retrieves the deformed Spline/LineObject
        deformedSpline = SplineInputGeneratorHelper.FinalSpline(childSplineClone)
        if deformedSpline is None:
            return None

        # Performs operation on the spline
        resSpline = SplineInputGeneratorHelper.OffsetSpline(deformedSpline, op[c4d.PY_OFFSETYSPLINE_OFFSET])

        # Updates dirtyCount for the child spline
        self._childContourDirty = childSpline.GetDirty(c4d.DIRTYFLAGS_DATA | c4d.DIRTYFLAGS_MATRIX | c4d.DIRTYFLAGS_CACHE)

        return resSpline


if __name__ == "__main__":
    c4d.plugins.RegisterObjectPlugin(id=PLUGIN_ID,
                                     str="Py-OffsetY",
                                     g=OffsetYSpline,
                                     description="py_offsets_y_spline",
                                     icon=None,
                                     info=c4d.OBJECT_GENERATOR | c4d.OBJECT_INPUT | c4d.OBJECT_ISSPLINE)
