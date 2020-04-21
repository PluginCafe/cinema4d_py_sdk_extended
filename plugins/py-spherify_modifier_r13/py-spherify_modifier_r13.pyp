"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam, Manuel MAGALHAES

Description:
    - Modifier, modifying a point object (like the bend deformer).
    - Supports Falloff (R19 and R20 only).

Class/method highlighted:
    - c4d.plugins.ObjectData
    - NodeData.Init()
    - NodeData.Message()
    - NodeData.GetDDescription()
    - NodeData.CopyTo()
    - ObjectData.ModifyObject()
    - ObjectData.GetDimension()
    - ObjectData.GetHandleCount()
    - ObjectData.GetHandle()
    - ObjectData.SetHandle()
    - ObjectData.Draw()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21
"""
import os
import sys
import c4d

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1025252


class SpherifyModifier(c4d.plugins.ObjectData):
    """Spherify Modifier"""

    HANDLECOUNT = 2

    def __init__(self, *args):
        self.SetOptimizeCache(True)
        self.falloff = None
        self.falloffDirty = True

    def Init(self, op):
        """
        Called when Cinema 4D Initialize the ObjectData (used to define, default values)
        :param node: The instance of the ObjectData.
        :type node: c4d.GeListNode
        :return: True on success, otherwise False.
        """
        self.InitAttr(op, float, c4d.PYSPHERIFYMODIFIER_RADIUS)
        self.InitAttr(op, float, c4d.PYSPHERIFYMODIFIER_STRENGTH)

        op[c4d.PYSPHERIFYMODIFIER_RADIUS] = 200.0
        op[c4d.PYSPHERIFYMODIFIER_STRENGTH] = 0.5

        # Assigns falloff
        if self.falloff is None and c4d.API_VERSION > 19000:
            self.falloff = c4d.modules.mograph.C4D_Falloff()
            if self.falloff is None:
                return False

        return True

    def Message(self, node, type, data):
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
        if type == c4d.MSG_MENUPREPARE:
            # Enables deform tick when created from UI
            node.SetDeformMode(True)

        # Passes message to falloff
        if self.falloff is not None:
            self.falloff.Message(type, node.GetDataInstance(), data)

        return True

    def CheckDirty(self, op, doc):
        """
        This Method is called automatically when Cinema 4D ask the object his dirtiness.
        If falloff changed, a new computation of the deformer is needed.
        :param op: The Python Generator 
        :type op: c4d.BaseObject.
        :param doc: The document containing the plugin object.
        :type doc: c4d.documents.BaseDocument 
        """
        if self.falloff is not None:
            # Gets the dirtiness of the falloff.
            dirty = self.falloff.GetDirty(op.GetDataInstance())
            # Checks if the dirty stats is the same stored
            if dirty != self.falloffDirty:
                # Stores the new dirty states and set the object dirty.
                self.falloffDirty = dirty
                op.SetDirty(c4d.DIRTYFLAGS_DATA)

    def GetDDescription(self, node, description, flags):
        """
        Called by Cinema 4D when the description (UI) is queried.
        :param node: The instance of the ObjectData.
        :type node: c4d.GeListNode
        :param description: The description to modify.
        :type description: c4d.Description
        :param flags: The flags for the description operation.
        :type flags: int
        :return: The success status or the data to be returned.
        :rtype: Union[Bool, tuple(bool, Any, DESCFLAGS_DESC)]
        """
        data = node.GetDataInstance()
        if data is None:
            return False

        # Loads Spherify Modifier description
        if not description.LoadDescription(node.GetType()):
            return False

        # Adds falloff UI to description
        if self.falloff is not None:
            if not self.falloff.SetMode(data.GetInt32(c4d.FALLOFF_MODE, c4d.FALLOFF_MODE_INFINITE), data):
                return False

            if not self.falloff.AddFalloffToDescription(description, data):
                return False

        return True, flags | c4d.DESCFLAGS_DESC_LOADED

    def CopyTo(self, dest, snode, dnode, flags, trn):
        """
        Called by Cinema 4D when the current object instance is copied.
        The purpose is to copy the member variable from source variable to destination variable.
        :param dest: The new instance of the ObjectData where the data need to be copied.
        :type dest: c4d.plugins.NodeData
        :param snode: The source node data, i.e. the current node.
        :type snode: c4d.GeListNode
        :param dnode: The new node data where the data need to be copied.
        :type dnode: c4d.GeListNode
        :param flags: the copy flags.
        :type flags: COPYFLAGS
        :param trn: An alias translator for the operation.
        :type trn: c4d.AliasTrans
        :return: True if the data was copied successfully, otherwise False.
        """

        if self.falloff is not None and dest.falloff is not None:
            # Copies falloff to destination Py-SpherifyModifier if needed
            if not self.falloff.CopyTo(dest.falloff):
                return False

        return True

    def ModifyObject(self, mod, doc, op, op_mg, mod_mg, lod, flags, thread):
        """
        Called by Cinema 4D with the object to modify.
        :param mod: The Python Modifier.
        :type mod: c4d.BaseObject
        :param doc: The document containing the plugin object.
        :type doc: c4d.documents.BaseDocument
        :param op: The object to modify.
        :type op: c4d.BaseObject
        :param op_mg: The object's world matrix.
        :type op_mg: c4d.Matrix
        :param mod_mg: The modifier object's world matrix.
        :type mod_mg: c4d.Matrix
        :param lod: The level of detail.
        :type lod: float
        :param flags: Currently unused.
        :type flags: int
        :param thread: The calling thread.
        :type thread: c4d.threading.BaseThread
        :return: True if the object was modified, otherwise False.
        """
        # Modifies the point object
        if not op.CheckType(c4d.Opoint):
            return True

        # Retrieves points
        points = op.GetAllPoints()

        # If there is no point, nothing to modify we leave
        if len(points) == 0:
            return True

        # Checks if falloff can be skiped
        skipFalloff = True
        if c4d.API_VERSION > 19000:
            skipFalloff = op[c4d.FALLOFF_MODE] == c4d.FALLOFF_MODE_INFINITE and op[c4d.FALLOFF_STRENGTH] == 1.0
        
        # Initializes fallof if needed
        if self.falloff is not None and not skipFalloff:
            if not self.falloff.InitFalloff(mod.GetDataInstance(), doc, mod):
                return False

        # Retrieves parameters
        radius = mod[c4d.PYSPHERIFYMODIFIER_RADIUS]
        strength = mod[c4d.PYSPHERIFYMODIFIER_STRENGTH]

        # Calculates a weight map, so weight map can drive the deformer
        weights = op.CalcVertexmap(mod)

        # Calculates spherify deformation
        matrix = ~mod_mg * op_mg
        invMatrix = ~matrix

        # Iterates overs each points to modify them
        for index, point in enumerate(points):

            # Retrieves position in Local post
            finalPoint = matrix * point

            # Check if there is a weight map
            finalStrength = strength
            if weights is not None:
                finalStrength *= weights[index]

            # Samples the falloff
            if self.falloff is not None and not skipFalloff:
                finalStrength *= self.falloff.Sample(op_mg * points[index])

            # Calculates the point position
            finalPoint = finalStrength * ((finalPoint.GetNormalized()) * radius) + (1.0 - finalStrength) * finalPoint

            # Defines the points position
            op.SetPoint(index, finalPoint * invMatrix)

        # Updates input object
        op.Message(c4d.MSG_UPDATE)

        return True

    def GetDimension(self, op, mp, rad):
        """
        Called By Cinema to retrieve the bounding box of the generated object (BaseObject.GetRad())
        :param op: The instance of the ObjectData.
        :type op: c4d.BaseObject
        :param mp: Assign the center point of the bounding box to this vector.
        :type mp: c4d.Vector
        :param rad: Assign the XYZ bounding box radius to this vector.
        :type rad: c4d.Vector
        """
        # Checks if one of theses value are None
        radius = op[c4d.PYSPHERIFYMODIFIER_RADIUS]
        if radius is None:
            return

        # Assigns the center point to 0.0
        mp = c4d.Vector()

        # Assigns the total radius
        rad = c4d.Vector(radius)

    """========== Start of Handle Management =========="""

    def GetHandleCount(self, op):
        """
        Called to get the number of handles the object has. Part of the automated handle interface.
        :param op: The instance of the ObjectData.
        :type op: c4d.BaseObject
        :return: The number of handles for the object.
        :rtype: int
        """
        if self.falloff is not None:
            return self.falloff.GetHandleCount(op.GetDataInstance()) + SpherifyModifier.HANDLECOUNT

        return SpherifyModifier.HANDLECOUNT

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
        # Retrieves parameters value from the generator object
        rad = op[c4d.PYSPHERIFYMODIFIER_RADIUS] if op[c4d.PYSPHERIFYMODIFIER_RADIUS] is not None else 200.0
        strength = op[c4d.PYSPHERIFYMODIFIER_STRENGTH] if op[c4d.PYSPHERIFYMODIFIER_STRENGTH] is not None else 0.5

        # According the HandleID we are asked , defines different position/direction.
        if i < self.HANDLECOUNT:
            if i == 0:
                # Radius handle
                info.position = c4d.Vector(rad, 0.0, 0.0)
                info.direction = c4d.Vector(1.0, 0.0, 0.0)
                info.type = c4d.HANDLECONSTRAINTTYPE_LINEAR
            elif i == 1:
                # Strength handle
                info.position = c4d.Vector(strength * 1000.0, 0.0, 0.0)
                info.direction = c4d.Vector(1.0, 0.0, 0.0)
                info.type = c4d.HANDLECONSTRAINTTYPE_LINEAR

        # Creates handle from the Fallof object
        else:
            # Falloff handles
            if self.falloff is not None:
                self.falloff.GetHandle(i - self.HANDLECOUNT, op.GetDataInstance(), info)

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
        if i < SpherifyModifier.HANDLECOUNT:
            val = p.x
            if i == 0:
                # Radius handle
                op[c4d.PYSPHERIFYMODIFIER_RADIUS] = val

            elif i == 1:
                # Strength handle
                op[c4d.PYSPHERIFYMODIFIER_STRENGTH] = c4d.utils.ClampValue(val * 0.001, 0.0, 1.0)
        else:
            # Falloff handles
            if self.falloff is not None:
                self.falloff.SetHandle(i - SpherifyModifier.HANDLECOUNT, p, op.GetDataInstance(), info)

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
        # If the current draw pass is for object drawing (polygon spline, etc)
        if drawpass == c4d.DRAWPASS_OBJECT:
            # Initialize the fallof if needed (skip if fallof is set to linear with 1.0 ratio)
            # Checks if falloff can be skiped
            skipFalloff = True
            if c4d.API_VERSION > 19000:
                skipFalloff = op[c4d.FALLOFF_MODE] == c4d.FALLOFF_MODE_INFINITE and op[c4d.FALLOFF_STRENGTH] == 1.0

            if self.falloff is not None and not skipFalloff:
                if not self.falloff.InitFalloff(op.GetDataInstance(), bh.GetDocument(), op):
                    return c4d.DRAWRESULT_ERROR

            # Retrieves the object color
            bd.SetPen(bd.GetObjectColor(bh, op))
            bd.SetMatrix_Matrix(None, c4d.Matrix())

            # Defines the scale/rotation where drawing will operate by the radius of the generator
            rad = op[c4d.PYSPHERIFYMODIFIER_RADIUS]
            m = bh.GetMg()

            # Draw the first circle
            m.v1 *= rad
            m.v2 *= rad
            m.v3 *= rad
            bd.DrawCircle(m)

            # Draw the second circle
            h = m.v2
            m.v2 = m.v3
            m.v3 = h
            bd.DrawCircle(m)

            # Draw the third circle
            h = m.v1
            m.v1 = m.v3
            m.v3 = h
            bd.DrawCircle(m)

            # If there is a fallof, draw the fallof
            if self.falloff is not None and not skipFalloff:
                self.falloff.Draw(bd, bh, drawpass, op.GetDataInstance())

                # Restores camera matrix as falloff changes this
                bd.SetMatrix_Camera()

        # If the current draw pass is for handle drawing
        elif drawpass == c4d.DRAWPASS_HANDLES:
            # Resets the matrix
            bd.SetMatrix_Matrix(None, bh.GetMg())

            # Checks if one of the handle of the current object is currently hovered by the mouse.
            hitId = op.GetHighlightHandle(bd)

            for i in range(SpherifyModifier.HANDLECOUNT):
                # Defines the color of the handle according of the hovered state of the object.
                hoverColor = c4d.VIEWCOLOR_ACTIVEPOINT if hitId != i else c4d.VIEWCOLOR_SELECTION_PREVIEW
                bd.SetPen(c4d.GetViewColor(hoverColor))

                # Retrieves the information of the current handle.
                info = c4d.HandleInfo()
                self.GetHandle(op, i, info)

                # Draws the handle to the correct position
                bd.DrawHandle(info.position, c4d.DRAWHANDLE_BIG, 0)

            # Draw the line to the second Handle
            bd.SetPen(c4d.GetViewColor(c4d.VIEWCOLOR_ACTIVEPOINT))
            bd.DrawLine(info.position, c4d.Vector(0), 0)

        # If the current draw pass is not the object or handle, skip this Draw Call.
        else:
            return c4d.DRAWRESULT_SKIP

        return c4d.DRAWRESULT_OK

    """========== End of Handle Management =========="""


if __name__ == "__main__":
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "opyspherifymodifier.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    # Registers the object plugin
    c4d.plugins.RegisterObjectPlugin(id=PLUGIN_ID,
                                 str="Py-SpherifyModifier",
                                 g=SpherifyModifier,
                                 description="opyspherifymodifier",
                                 icon=bmp,
                                 info=c4d.OBJECT_MODIFIER)
