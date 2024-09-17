"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam

Description:
    - Generator, generating a c4d.PolygonObject from nothing (like the Cube).
    - Manages handles to drive parameters (works only in R18+).

Class/method highlighted:
    - c4d.plugins.ObjectData
    - NodeData.Init()
    - ObjectData.GetDimension()
    - ObjectData.GetVirtualObjects()
    - ObjectData.GetHandleCount()
    - ObjectData.GetHandle()
    - ObjectData.SetHandle()
    - ObjectData.Draw()

"""
import os
import math
import sys
import c4d

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1025250


class RoundedTubeHelper(object):

    @staticmethod
    def SetAxis(op, axis):
        """Rotates all points of an object in a given plane coordinate.

        Args:
            op (c4d.PolygonObject): The object to modifiy
            axis (PRIM_AXIS): The axis to convert the coordinate

        Returns:
            bool: Success of the operation
        """
        if axis == c4d.PRIM_AXIS_YP:
            return False

        pList = op.GetAllPoints()
        if pList is None:
            return False

        elif axis == c4d.PRIM_AXIS_XP:
            for i, p in enumerate(pList):
                op.SetPoint(i, c4d.Vector(p.y, -p.x, p.z))

        elif axis == c4d.PRIM_AXIS_XN:
            for i, p in enumerate(pList):
                op.SetPoint(i, c4d.Vector(-p.y, p.x, p.z))

        elif axis == c4d.PRIM_AXIS_YN:
            for i, p in enumerate(pList):
                op.SetPoint(i, c4d.Vector(-p.x, -p.y, p.z))

        elif axis == c4d.PRIM_AXIS_ZP:
            for i, p in enumerate(pList):
                op.SetPoint(i, c4d.Vector(p.x, -p.z, p.y))

        elif axis == c4d.PRIM_AXIS_ZN:
            for i, p in enumerate(pList):
                op.SetPoint(i, c4d.Vector(p.x, p.z, -p.y))

        op.Message(c4d.MSG_UPDATE)
        return True

    @staticmethod
    def SwapPoint(p, axis):
        """Swap a vector according a working plane.

        Args:
            p (c4d.Vector): the position in PRIM_AXIS_YP plane
            axis (PRIM_AXIS): The axis to convert the coordinate

        Returns:
            c4d.Vector: The position in the desired plane coordinate
        """
        if axis == c4d.PRIM_AXIS_XP:
            return c4d.Vector(p.y, -p.x, p.z)
        elif axis == c4d.PRIM_AXIS_XN:
            return c4d.Vector(-p.y, p.x, p.z)
        elif axis == c4d.PRIM_AXIS_YN:
            return c4d.Vector(-p.x, -p.y, p.z)
        elif axis == c4d.PRIM_AXIS_ZP:
            return c4d.Vector(p.x, -p.z, p.y)
        elif axis == c4d.PRIM_AXIS_ZN:
            return c4d.Vector(p.x, p.z, -p.y)
        return p

    def GenerateLathe(self, srcPtList, srcPtCount, srcSub):
        # Defines how many points and polygons the final polygon object will be
        ptCount = srcPtCount * srcSub
        polyCount = srcPtCount * srcSub

        # Creates a Polygon Object
        op = c4d.PolygonObject(ptCount, polyCount)
        if op is None:
            raise MemoryError("Failed to create a Polygon Object.")

        # Defines the length according subdivision
        uvadr = [0.0] * (srcPtCount + 1)
        length = 0.0
        for i in range(srcPtCount):
            uvadr[i] = length
            length += (srcPtList[(i + 1) % srcPtCount] - srcPtList[i]).GetLength()

        if length > 0.0:
            length = 1.0 / length

        for i in range(srcPtCount):
            uvadr[i] *= length

        uvadr[srcPtCount] = 1.0
        polyCount = 0
        for i in range(srcSub):
            sn, cs = c4d.utils.SinCos(math.pi * 2 * float(i) / float(srcSub))
            v1 = float(i) / float(srcSub)
            v2 = float(i+1) / float(srcSub)
            for j in range(srcPtCount):
                a = srcPtCount * i + j
                op.SetPoint(a, c4d.Vector(srcPtList[j].x * cs, srcPtList[j].y, srcPtList[j].x * sn))
                if i < srcSub:
                    b = srcPtCount * i + ((j + 1) % srcPtCount)
                    c = srcPtCount * ((i + 1) % srcSub) + ((j + 1) % srcPtCount)
                    d = srcPtCount * ((i + 1) % srcSub) + j
                    pol = c4d.CPolygon(a, b, c, d)
                    op.SetPolygon(polyCount, pol)
                    polyCount += 1

        # Notifies the polygon object its structure changed
        op.Message(c4d.MSG_UPDATE)

        # Defines the Phong shading of the generated object
        op.SetPhong(True, True, c4d.utils.Rad(80.0))

        return op


class RoundedTube(c4d.plugins.ObjectData, RoundedTubeHelper):
    """RoundedTube Generator"""

    HANDLECOUNT = 5

    def __init__(self, *args):
        super(RoundedTube, self).__init__(*args)
        self.SetOptimizeCache(True)

    def Init(self, op, isCloneInit=False):
        """Called when Cinema 4D Initialize the ObjectData (used to define, default values).

        Args:
            op: (c4d.GeListNode): The instance of the ObjectData.
            isCloneInit (bool): True if the object data is a copy of another one.

        Returns:
            bool: True on success, otherwise False.
        """
        self.InitAttr(op, float, c4d.PY_TUBEOBJECT_RAD)
        self.InitAttr(op, float, c4d.PY_TUBEOBJECT_IRADX)
        self.InitAttr(op, float, c4d.PY_TUBEOBJECT_IRADY)
        self.InitAttr(op, float, c4d.PY_TUBEOBJECT_SUB)
        self.InitAttr(op, int, c4d.PY_TUBEOBJECT_ROUNDSUB)
        self.InitAttr(op, float, c4d.PY_TUBEOBJECT_ROUNDRAD)
        self.InitAttr(op, int, c4d.PY_TUBEOBJECT_SEG)
        self.InitAttr(op, int, c4d.PRIM_AXIS)

        if not isCloneInit:
            op[c4d.PY_TUBEOBJECT_RAD] = 200.0
            op[c4d.PY_TUBEOBJECT_IRADX] = 50.0
            op[c4d.PY_TUBEOBJECT_IRADY] = 50.0
            op[c4d.PY_TUBEOBJECT_SUB] = 1
            op[c4d.PY_TUBEOBJECT_ROUNDSUB] = 8
            op[c4d.PY_TUBEOBJECT_ROUNDRAD] = 10.0
            op[c4d.PY_TUBEOBJECT_SEG] = 36
            op[c4d.PRIM_AXIS] = c4d.PRIM_AXIS_YP
        return True

    def GetDimension(self, op, mp, rad):
        """Called By Cinema to retrieve the bounding box of the generated object (BaseObject.GetRad())

        Args:
            op (c4d.BaseObject): The instance of the ObjectData.
            mp (c4d.Vector): Assign the center point of the bounding box to this vector.
            rad (c4d.Vector): Assign the XYZ bounding box radius to this vector.
        """
        # Retrieves generator parameters
        rado = op[c4d.PY_TUBEOBJECT_RAD]
        radx = op[c4d.PY_TUBEOBJECT_IRADX]
        rady = op[c4d.PY_TUBEOBJECT_IRADY]
        axis = op[c4d.PRIM_AXIS]

        # Checks if one of theses value are None
        if None in [rado, radx, rady, axis]:
            return

        # Assigns the center point to 0.0
        mp = c4d.Vector(0.0)

        # Assigns the total radius
        if axis == c4d.PRIM_AXIS_XP or axis == c4d.PRIM_AXIS_XN:
            rad.x = rady
            rad.y = rado + radx
            rad.z = rado + radx
        elif axis == c4d.PRIM_AXIS_YP or axis == c4d.PRIM_AXIS_YN:
            rad.x = rado + radx
            rad.y = rady
            rad.z = rado + radx
        elif axis == c4d.PRIM_AXIS_ZP or axis == c4d.PRIM_AXIS_ZN:
            rad.x = rado + radx
            rad.y = rado + radx
            rad.z = rady

    def GetVirtualObjects(self, op, hierarchyhelp):
        """This method is called automatically when Cinema 4D ask for the cache of an object. 

        This is also the place where objects have to be marked as input object by Touching them (destroy their cache in order to disable them in Viewport)

        Args:
            op (c4d.BaseObject.): The Python Generator
            hierarchyhelp (c4d.HierarchyHelp): The hierarchy helper.

        Returns:
            The Representing object (c4d.LineObject or SplineObject)
        """
        # Disable the following lines because cache flag was set
        # So the cache build is done before this method is called
        # dirty = op.CheckCache(hierarchyhelp) or op.IsDirty(c4d.DIRTYFLAGS_DATA)
        # if dirty is False: return op.GetCache(hierarchyhelp)

        # Retrieves parameters value from the generator object
        rad = op[c4d.PY_TUBEOBJECT_RAD] if op[c4d.PY_TUBEOBJECT_RAD] is not None else 200.0
        iradx = op[c4d.PY_TUBEOBJECT_IRADX] if op[c4d.PY_TUBEOBJECT_IRADX] is not None else 50.0
        irady = op[c4d.PY_TUBEOBJECT_IRADY] if op[c4d.PY_TUBEOBJECT_IRADY] is not None else 50.0
        rrad = op[c4d.PY_TUBEOBJECT_ROUNDRAD] if op[c4d.PY_TUBEOBJECT_ROUNDRAD] is not None else 10.0
        num_sub = op[c4d.PY_TUBEOBJECT_SUB] if op[c4d.PY_TUBEOBJECT_SUB] is not None else 1
        num_rsub = op[c4d.PY_TUBEOBJECT_ROUNDSUB] if op[c4d.PY_TUBEOBJECT_ROUNDSUB] is not None else 8
        num_seg = op[c4d.PY_TUBEOBJECT_SEG] if op[c4d.PY_TUBEOBJECT_SEG] is not None else 36

        # Calculates LOD for subdivision parameter
        sub = c4d.utils.CalcLOD(num_sub, 1, 1, 1000)
        rsub = c4d.utils.CalcLOD(num_rsub, 1, 1, 1000)
        seg = c4d.utils.CalcLOD(num_seg, 1, 3, 1000)

        # Defines list of vector position of points
        ptCount = 4 * (sub + rsub)
        ptList = [c4d.Vector()] * ptCount

        # Defines position for side points
        for i in range(sub):
            ptList[i] = c4d.Vector(rad - iradx, (1.0 - float(i) / sub * 2.0) * (irady - rrad), 0.0)
            ptList[i + sub + rsub] = c4d.Vector(rad + (float(i) / sub * 2.0 - 1.0) * (iradx - rrad), -irady, 0.0)
            ptList[i + 2 * (sub + rsub)] = c4d.Vector(rad + iradx, (float(i) / float(sub) * 2.0 - 1.0) * (irady - rrad), 0.0)
            ptList[i + 3 * (sub + rsub)] = c4d.Vector(rad + (1.0 - float(i) / float(sub) * 2.0) * (iradx - rrad), irady, 0.0)

        # Defines position for the top / bottom fillet cap points
        pi05 = 1.570796326
        for i in range(rsub):
            sn, cs = c4d.utils.SinCos(float(i) / rsub * pi05)
            ptList[i + sub] = c4d.Vector(rad - (iradx - rrad + cs * rrad), -(irady - rrad + sn * rrad), 0.0)
            ptList[i + sub + (sub + rsub)] = c4d.Vector(rad + (iradx - rrad + sn * rrad), -(irady - rrad + cs * rrad), 0.0)
            ptList[i + sub + 2 * (sub + rsub)] = c4d.Vector(rad + (iradx - rrad + cs * rrad), + (irady - rrad + sn * rrad), 0.0)
            ptList[i + sub + 3 * (sub + rsub)] = c4d.Vector(rad - (iradx - rrad + sn * rrad), + (irady - rrad + cs * rrad), 0.0)

        # Generates the polygons
        ret = self.GenerateLathe(ptList, ptCount, seg)
        if ret is None:
            return None

        # Orients the generates object in the correct planes
        axis = op[c4d.PRIM_AXIS] if op[c4d.PRIM_AXIS] is not None else c4d.PRIM_AXIS_YP
        RoundedTube.SetAxis(ret, axis)

        # Defines the name of the generated object as the same of the generator
        ret.SetName(op.GetName())

        # Returns the generated objects.
        return ret
    """========== Start of Handle Management =========="""

    def GetHandleCount(self, op):
        return self.HANDLECOUNT

    def GetHandle(self, op, i, info):
        """Called by Cinema 4D to retrieve the information of a given handle ID to represent a/some parameter(s).

        Args:
            op (c4d.BaseObject): The instance of the ObjectData.
            i (int): The handle index.
            info (c4d.HandleInfo): The HandleInfo to fill with data.
        """

        # Retrieves parameters value from the generator object
        rad = op[c4d.PY_TUBEOBJECT_RAD] if op[c4d.PY_TUBEOBJECT_RAD] is not None else 200.0
        iradx = op[c4d.PY_TUBEOBJECT_IRADX] if op[c4d.PY_TUBEOBJECT_IRADX] is not None else 50.0
        irady = op[c4d.PY_TUBEOBJECT_IRADY] if op[c4d.PY_TUBEOBJECT_IRADY] is not None else 50.0
        rrad = op[c4d.PY_TUBEOBJECT_ROUNDRAD] if op[c4d.PY_TUBEOBJECT_ROUNDRAD] is not None else 10.0
        axis = op[c4d.PRIM_AXIS] if op[c4d.PRIM_AXIS] is not None else c4d.PRIM_AXIS_YP

        # According the HandleID we are asked , defines different position/direction.
        if i == 0:
            info.position = c4d.Vector(rad, 0.0, 0.0)
            info.direction = c4d.Vector(1.0, 0.0, 0.0)
        elif i == 1:
            info.position = c4d.Vector(rad+iradx, 0.0, 0.0)
            info.direction = c4d.Vector(1.0, 0.0, 0.0)
        elif i == 2:
            info.position = c4d.Vector(rad, irady, 0.0)
            info.direction = c4d.Vector(0.0, 1.0, 0.0)
        elif i == 3:
            info.position = c4d.Vector(rad+iradx, irady-rrad, 0.0)
            info.direction = c4d.Vector(0.0, -1.0, 0.0)
        elif i == 4:
            info.position = c4d.Vector(rad+iradx-rrad, irady, 0.0)
            info.direction = c4d.Vector(-1.0, 0.0, 0.0)

        # Finally set the points according the plane the generator is asked to generate
        info.position = RoundedTube.SwapPoint(info.position, axis)
        info.direction = RoundedTube.SwapPoint(info.direction, axis)
        info.type = c4d.HANDLECONSTRAINTTYPE_LINEAR

    def SetHandle(self, op, i, p, info):
        """Called by Cinema 4D when the user set the handle.

        This is the place to retrieve the information of a given handle ID and drive your parameter(s).

        Args:
            op (c4d.BaseObject): The instance of the ObjectData.
            i (int): The handle index.
            p (c4d.Vector): The new Handle Position.
            info (c4d.HandleInfo): The HandleInfo filled with data.
        """
        # Creates a HandleInfo
        tmp = c4d.HandleInfo()

        # Fill it with the current data
        self.GetHandle(op, i, tmp)

        # Retrieves the value
        val = (p-tmp.position) * info.direction

        # According the current HandleID
        if i == 0:
            op[c4d.PY_TUBEOBJECT_RAD] = c4d.utils.FCut(op[c4d.PY_TUBEOBJECT_RAD]+val, op[c4d.PY_TUBEOBJECT_IRADX], sys.maxsize)
        elif i == 1:
            op[c4d.PY_TUBEOBJECT_IRADX] = c4d.utils.FCut(op[c4d.PY_TUBEOBJECT_IRADX]+val, op[c4d.PY_TUBEOBJECT_ROUNDRAD], op[c4d.PY_TUBEOBJECT_RAD])
        elif i == 2:
            op[c4d.PY_TUBEOBJECT_IRADY] = c4d.utils.FCut(op[c4d.PY_TUBEOBJECT_IRADY]+val, op[c4d.PY_TUBEOBJECT_ROUNDRAD], sys.maxsize)
        elif i == 3 or i == 4:
            op[c4d.PY_TUBEOBJECT_ROUNDRAD] = c4d.utils.FCut(op[c4d.PY_TUBEOBJECT_ROUNDRAD]+val, 0.0, min(op[c4d.PY_TUBEOBJECT_IRADX], op[c4d.PY_TUBEOBJECT_IRADY]))

    def Draw(self, op, drawpass, bd, bh):
        """Called by Cinema 4D when the display is updated to display some visual element of your object in the 3D view.
        
        This is also the place to draw handles

        Args:
            op (c4d.BaseObject): The instance of the ObjectData.
            drawpass (int): The current draw pass.
            bd (c4d.BaseDraw): The editor's view.
            bh (c4d.plugins.BaseDrawHelp): The BaseDrawHelp editor's view.

        Returns:
            bool: The result of the drawing (most likely c4d.DRAWRESULT_OK)
        """
        # If the current draw pass is not the handle, skip this Draw Call.
        if drawpass != c4d.DRAWPASS_HANDLES:
            return c4d.DRAWRESULT_SKIP

        rad = op[c4d.PY_TUBEOBJECT_RAD]
        iradx = op[c4d.PY_TUBEOBJECT_IRADX]
        irady = op[c4d.PY_TUBEOBJECT_IRADY]
        axis = op[c4d.PRIM_AXIS]

        # Defines the drawing matrix to the object matrix.
        m = bh.GetMg()
        bd.SetMatrix_Matrix(op, m)

        # Checks if one of the handle of the current object is currently hovered by the mouse.
        hitId = op.GetHighlightHandle(bd)

        # Iterates over our handle count and draw them
        for i in range(self.HANDLECOUNT):
            # Defines the color of the handle according of the hovered state of the object.
            handleColorFlag = c4d.VIEWCOLOR_HANDLES if c4d.GetC4DVersion() >= 21000 else c4d.VIEWCOLOR_ACTIVEPOINT
            hoverColor = c4d.VIEWCOLOR_SELECTION_PREVIEW if hitId == i else handleColorFlag
            bd.SetPen(c4d.GetViewColor(hoverColor), 0)

            # Retrieves the information of the current handle.
            info = c4d.HandleInfo()
            self.GetHandle(op, i, info)

            # Draws the handle to the correct position
            bd.DrawHandle(info.position, c4d.DRAWHANDLE_BIG, 0)

            # Sets the color back to normal before drawing lines
            bd.SetPen(c4d.GetViewColor(handleColorFlag), 0)
            
            # Draws the lines 0, 1, 2 are draw in the same drawcall
            if i == 0:
                info2 = c4d.HandleInfo()
                self.GetHandle(op, 1, info2)
                bd.DrawLine(info.position, info2.position, 0)
                self.GetHandle(op, 2, info2)
                bd.DrawLine(info.position, info2.position, 0)
            elif i == 3:
                bd.DrawLine(info.position, RoundedTube.SwapPoint(c4d.Vector(rad+iradx, irady, 0.0), axis), 0)
            elif i == 4:
                bd.DrawLine(info.position, RoundedTube.SwapPoint(c4d.Vector(rad+iradx, irady, 0.0), axis), 0)

        return c4d.DRAWRESULT_OK
    """========== End of Handle Management =========="""


if __name__ == "__main__":
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "oroundedtube.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    # Registers the object plugin
    c4d.plugins.RegisterObjectPlugin(id=PLUGIN_ID,
                                     str="Py-RoundedTube",
                                     g=RoundedTube,
                                     description="roundedtube",
                                     icon=bmp,
                                     info=c4d.OBJECT_GENERATOR)
