"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam

Description:
    - Generator, generating a c4d.SplineObject from nothing (like the spline circle).
    - Consists of two circles in a given plane.
    - Manages handles to drive parameters.
    - Registers Help Callback to display user help, if the user click on show help of a parameter.

Class/method highlighted:
    - c4d.plugins.ObjectData
    - ObjectData.Init()
    - ObjectData.GetDEnabling()
    - ObjectData.Message()
    - ObjectData.GetContour()
    - ObjectData.GetHandle()
    - ObjectData.SetHandle()
    - ObjectData.Draw()
    - c4d.plugins.RegisterPluginHelpCallback()

Compatible:
    - Win / Mac
    - R19, R20, R21
"""
import sys
import os
import math
import c4d

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1025245


class DoubleCircleHelper(object):

    @staticmethod
    def SwapPoint(p, plane):
        if plane == c4d.PRIM_PLANE_XY:
            return p
        if plane == c4d.PRIM_PLANE_ZY:
            return c4d.Vector(-p.z, p.y, p.x)
        elif plane == c4d.PRIM_PLANE_XZ:
            return c4d.Vector(p.x, -p.z, p.y)
        else:
            raise ValueError("Plane ID should be 0, 1 or 2.")

    @classmethod
    def GenerateCircle(cls, radius, plane=c4d.PRIM_PLANE_XY):
        """
        Generates a circle spline of a given radius
        :param radius: The radius of the circle to be created.
        :type radius: float
        :param plane: The axis plane to be used. PRIM_PLANE_XY, PRIM_PLANE_ZY or PRIM_PLANE_XZ
        :type plane: int
        :return: The generates Circle or None if fail.
        :rtype: Union[c4d.SplineObject, None]
        """
        sub = 4
        TANG = 0.415

        # Creates a SplineObject
        splineObject = c4d.SplineObject(sub * 2, c4d.SPLINETYPE_BEZIER)
        if splineObject is None:
            raise MemoryError("Failed to create a SplineObject.")

        # Defines 2 segments in the spline object
        splineObject.MakeVariableTag(c4d.Tsegment, 2)

        # Sets the spline to be closed
        splineObject[c4d.SPLINEOBJECT_CLOSED] = True

        # Checks segments counts are correct, if not something wrong happens.
        segCount = splineObject.GetSegmentCount()
        if segCount == 0:
            return None

        # Defines for each segment, the points used and the closed state of each segment
        splineObject.SetSegment(id=0, cnt=4, closed=True)
        splineObject.SetSegment(id=1, cnt=4, closed=True)

        # Loops over each point of a circle
        for i in range(sub):
            sn, cs = c4d.utils.SinCos(2.0 * math.pi * i / float(sub))
            # Defines the point position of the outside and inner circle
            posOut = c4d.Vector(cs * radius, sn * radius, 0.0)
            posIn = posOut * 0.5

            splineObject.SetPoint(i, cls.SwapPoint(posOut, plane))
            splineObject.SetPoint(i + sub, cls.SwapPoint(posIn, plane))

            # Defines the tangent  of the outside and inner circle
            vlOut = c4d.Vector(sn * radius * TANG, -cs * radius * TANG, 0.0)
            vrOut = -vlOut
            vlIn = vlOut * 0.5
            vrIn = -vlIn

            splineObject.SetTangent(i, cls.SwapPoint(vlOut, plane), cls.SwapPoint(vrOut, plane))
            splineObject.SetTangent(i + sub, cls.SwapPoint(vlIn, plane), cls.SwapPoint(vrIn, plane))

        # Notifies the object, some updates have been made
        splineObject.Message(c4d.MSG_UPDATE)
        return splineObject

    @staticmethod
    def ReversePointOrder(op):
        """
        Reverses the points order SplineObject
        :param op: the SplineObject to be reversed
        :type op: c4d.SplineObject
        :return: True if point order have been reversed, otherwise False.
        """
        # Checks if the object have points
        pointCount = op.GetPointCount()
        if pointCount == 0:
            return False

        # Retrieves all points
        points = op.GetAllPoints()
        if not points:
            return False

        # Divides by 2 the total point number (for inner and outer spline)
        to = pointCount / float(2)
        if pointCount % 2:
            to += 1

        # Loops overs half of the point
        for i, point in enumerate(points[:int(to)]):
            # Defines the outside and inner point
            op.SetPoint(i, points[pointCount - 1 - i])
            op.SetPoint(pointCount - 1 - i, point)

            # Retrieves the tangent
            h = op.GetTangent(i)
            tangents = op.GetTangent(pointCount - 1 - i)
            # Move from right to left
            vr, vl = tangents["vl"], tangents["vr"]

            # Defines the outside and inner tangent
            op.SetTangent(i, vl, vr)
            op.SetTangent(pointCount - 1 - i, h["vr"], h["vl"])

        # Notifies the object, some updates have been made
        op.Message(c4d.MSG_UPDATE)
        return True


class DoubleCircleData(c4d.plugins.ObjectData, DoubleCircleHelper):
    """CircleObject Generator"""

    def Init(self, node):
        """
        Called when Cinema 4D Initialize the ObjectData (used to define, default values)
        :param node: The instance of the ObjectData.
        :type node: c4d.GeListNode
        :return: True on success, otherwise False.
        """
        # Retrieves the BaseContainer Instance to set the default values
        data = node.GetDataInstance()
        if data is None:
            return False

        # Defines default values in the BaseContainer
        data.SetFloat(c4d.PYCIRCLEOBJECT_RAD, 200.0)
        data.SetInt32(c4d.PRIM_PLANE, c4d.PRIM_PLANE_XY)
        data.SetBool(c4d.PRIM_REVERSE, False)
        data.SetInt32(c4d.SPLINEOBJECT_INTERPOLATION, c4d.SPLINEOBJECT_INTERPOLATION_ADAPTIVE)
        data.SetInt32(c4d.SPLINEOBJECT_SUB, 8)
        data.SetFloat(c4d.SPLINEOBJECT_ANGLE, c4d.utils.Rad(5.0))
        data.SetFloat(c4d.SPLINEOBJECT_MAXIMUMLENGTH, 5.0)
        return True

    def GetContour(self, node, doc, lod, bt):
        """
        Called by Cinema 4D to generate the output spline. Take care this function is called in a Threading context.
        No modification of the document is allowed here, only reading.
        :param node: The instance of the ObjectData.
        :type node: c4d.BaseObject
        :param doc: The active document, the instance of the ObjectData is currently in.
        :type doc: c4d.documents.BaseDocument
        :param lod: The level of detail
        :type lod: int
        :param bt: The thread that currently process the Generator
        :type bt: c4d.threading.BaseThread
        :return: Union[c4d.SplineObject, None]
        """
        # Checks if there is an active object
        if node is None:
            raise RuntimeError("node is None, should never happens, that means there is no generator.")

        # Generates a Spline Object in Memory according the correct radius and plane
        spline = self.GenerateCircle(node[c4d.PYCIRCLEOBJECT_RAD], node[c4d.PRIM_PLANE])
        if not spline:
            return None

        # Reverse point order if it's asked
        if node[c4d.PRIM_REVERSE]:
            DoubleCircleData.ReversePointOrder(spline)

        # Returns the spline
        return spline

    def Message(self, node, msgId, data):
        """
        Called by Cinema 4D part to notify the object to a special event
        :param node: The instance of the ObjectData.
        :type node: c4d.BaseObject
        :param msgId: The message ID type.
        :type msgId: int
        :param data: The message data.
        :type data: Any, depends of the message passed.
        :return: Depends of the message type, most of the time True.
        """
        # MSG_MENUPREPARE is received when called from the menu, to let some setup work.
        # In the case of this message, the data passed is the BaseDocument the object is inserted
        if msgId == c4d.MSG_MENUPREPARE:
            doc = data
            # Retrieves the plane ID in which the splines are created by default in this document, such as XY plane.
            node[c4d.PRIM_PLANE] = doc.GetSplinePlane()
        return True

    def GetDEnabling(self, node, id, t_data, flags, itemdesc):
        """
        Called  by Cinema 4D to decide which parameters should be enabled or disabled (ghosted).
        :param node: The instance of the ObjectData.
        :type node: c4d.BaseObject
        :param id: The Description ID of the parameter
        :type id: c4d.DescID
        :param t_data: The current data for the parameter.
        :type: t_data: Any.
        :param flags: Not used
        :param itemdesc: The description, encoded to a container
        :type itemdesc: c4d.BaseContainer
        :return: True if the parameter should be enabled, otherwise False.
        """
        # Retrieves the current interpolation
        inter = node[c4d.SPLINEOBJECT_INTERPOLATION]

        # Defines enable state for Spline number points parameter
        if id[0].id == c4d.SPLINEOBJECT_SUB:
            return inter == c4d.SPLINEOBJECT_INTERPOLATION_NATURAL or inter == c4d.SPLINEOBJECT_INTERPOLATION_UNIFORM

        # Defines enable state for Spline angle parameter
        elif id[0].id == c4d.SPLINEOBJECT_ANGLE:
            return inter == c4d.SPLINEOBJECT_INTERPOLATION_ADAPTIVE or inter == c4d.SPLINEOBJECT_INTERPOLATION_SUBDIV

        # Defines enable state for Spline maximum length parameter
        elif id[0].id == c4d.SPLINEOBJECT_MAXIMUMLENGTH:
            return inter == c4d.SPLINEOBJECT_INTERPOLATION_SUBDIV
        return True

    """========== Start of Handle Management =========="""

    def GetHandleCount(self, op):
        """
        Called by Cinema 4D to retrieve the count of Handle the object will have.
        :param op: The instance of the ObjectData.
        :type op: c4d.BaseObject
        :return: The number of handle
        :rtype: int
        """
        # One handle will be used for this object
        return 1

    def GetHandle(self, op, i, info):
        """
        Called by Cinema 4D to retrieve the information of a given handle ID to represent a/some parameter(s).
        :param op: The instance of the ObjectData.
        :type op: c4d.BaseObject
        :param i: The handle index.
        :type i: int
        :param info: The HandleInfo to fill with data.
        :type info: c4d.HandleInfo
        """
        # Retrieves the current BaseContainer
        data = op.GetDataInstance()
        if data is None:
            return

        # Retrieves parameters of the object.
        rad = data.GetFloat(c4d.PYCIRCLEOBJECT_RAD)
        plane = data.GetInt32(c4d.PRIM_PLANE)

        # Defines the position, direction and type of the handle
        info.position = DoubleCircleData.SwapPoint(c4d.Vector(rad, 0.0, 0.0), plane)
        info.direction = ~DoubleCircleData.SwapPoint(c4d.Vector(1.0, 0.0, 0.0), plane)
        info.type = c4d.HANDLECONSTRAINTTYPE_LINEAR

    def SetHandle(self, op, i, p, info):
        """
        Called by Cinema 4D when the user set the handle.
        This is the place to retrieve the information of a given handle ID and drive your parameter(s).
        :param op: The instance of the ObjectData.
        :type op: c4d.BaseObject
        :param i: The handle index.
        :type i: int
        :param p: The new Handle Position.
        :type p: c4d.Vector
        :param info: The HandleInfo filled with data.
        :type info: c4d.HandleInfo
        """
        data = op.GetDataInstance()
        if data is None:
            return

        val = p * info.direction

        data.SetFloat(c4d.PYCIRCLEOBJECT_RAD, c4d.utils.FCut(val, 0.0, sys.maxsize))

    def Draw(self, op, drawpass, bd, bh):
        """
        Called by Cinema 4d when the display is updated to display some visual element of your object in the 3D view.
        This is also the place to draw Handle
        :param op: The instance of the ObjectData.
        :type op: c4d.BaseObject
        :param drawpass:
        :param bd: The editor's view.
        :type bd: c4d.BaseDraw
        :param bh: The BaseDrawHelp editor's view.
        :type bh: c4d.plugins.BaseDrawHelp
        :return: The result of the drawing (most likely c4d.DRAWRESULT_OK)
        """
        # If the current draw pass is not the handle, skip this Draw Call.
        if drawpass != c4d.DRAWPASS_HANDLES:
            return c4d.DRAWRESULT_SKIP

        # Defines the drawing matrix to the object matrix.
        m = bh.GetMg()
        bd.SetMatrix_Matrix(op, m)

        # Checks if one of the handle of the current object is currently hovered by the mouse.
        hitId = op.GetHighlightHandle(bd)

        # Defines the color of the handle according of the hovered state of the object.
        hoverColor = c4d.VIEWCOLOR_ACTIVEPOINT if hitId != 0 else c4d.VIEWCOLOR_SELECTION_PREVIEW
        bd.SetPen(c4d.GetViewColor(hoverColor))

        # Retrieves the information of the current handle.
        info = c4d.HandleInfo()
        self.GetHandle(op, 0, info)

        # Draw the handle to the correct position
        bd.DrawHandle(info.position, c4d.DRAWHANDLE_BIG, 0)
        bd.SetPen(c4d.GetViewColor(c4d.VIEWCOLOR_ACTIVEPOINT))
        bd.DrawLine(info.position, c4d.Vector(0), 0)

        return c4d.DRAWRESULT_OK

    """========== End of Handle Management =========="""


def DoubleCircleHelp(opType, baseType, group, property):
    """
    Called by Cinema 4D when the user use the help (Right Click - Show Help) on a parameter
    :param opType: The node type name, for example "OPYDOUBLECIRCLE"
    :type opType: str
    :param baseType: The name of the base object type that opType is derived from, usually the same as opType.
    :type baseType: str
    :param group: The name of the group in the attribute manager, for example "ID_OBJECTPROPERTIES".
    :type group: str
    :param property: The symbol name of the property, for example "PYCIRCLEOBJECT_RAD".
    :type property: str
    :return:
    """
    # Prints the information passed to the plugin help callback
    print("Py-DoubleCircle - Help:", opType, baseType, group, property)

    # If the users ask for help in the Radius Parameter
    if property == "PYCIRCLEOBJECT_RAD":
        # Displays a MessageDialog. An URL to online or local help could be opened in a browser
        c4d.gui.MessageDialog("Py - DoubleCircle - Radius of the Double Circle")

    return True


if __name__ == "__main__":
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "circle.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    # Registers the object plugin
    c4d.plugins.RegisterObjectPlugin(id=PLUGIN_ID,
                                     str="Py-DoubleCircle",
                                     g=DoubleCircleData,
                                     description="Opydoublecircle",
                                     icon=bmp,
                                     info=c4d.OBJECT_GENERATOR | c4d.OBJECT_ISSPLINE)

    # Registers the plugin help callback for Py-DoubleCircle
    c4d.plugins.RegisterPluginHelpCallback(PLUGIN_ID, DoubleCircleHelp)
