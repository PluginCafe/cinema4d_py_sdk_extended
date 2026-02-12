"""Demonstrates how to implement a deformer object.

Implements a simple deformer that deforms a point object by pushing its points to a spherical shape. 
The deformation is driven by two parameters, the radius of the sphere and the strength of the deformation.

Subjects:
    - Using ObjectData.ModifyObject() to modify an input object.
    - Handle management with GetHandleCount(), GetHandle() and SetHandle() to drive parameters with handles.
"""
__copyright__ = "Copyright 2026, MAXON Computer"
__author__ = "Ferdinand Hoppe, Maxime Adam"
__date__ = "12/02/2026"
__license__ = "Apache-2.0 license"

import os
import c4d

# Be sure to use a unique ID obtained from developers.maxon.net
PLUGIN_ID = 1025252

class SpherifyModifier(c4d.plugins.ObjectData):
    """Implements a simple deformer that deforms a point object by pushing its points to a 
    spherical shape. 
    
    The deformation is driven by two parameters, the radius of the sphere and the strength of the 
    deformation. The deformation work happens in the ModifyObject() method, which is called by 
    Cinema 4D with the object to modify. In order for an `OBjectData` to be able to modify an input 
    object, the plugin must be registered with the flag `c4d.OBJECT_MODIFIER`. This is done at the 
    end of this file in the call to `c4d.plugins.RegisterObjectPlugin()`.
    """

    HANDLECOUNT = 2

    def __init__(self, *args):
        self.SetOptimizeCache(True)

    def Init(self, op, isCloneInit=False):
        """Called when Cinema 4D Initialize the ObjectData (used to define, default values).

        Args:
            op: (c4d.GeListNode): The instance of the ObjectData.
            isCloneInit (bool): True if the object data is a copy of another one.

        Returns:
            True on success, otherwise False.
        """
        self.InitAttr(op, float, c4d.PY_SPHERE_DEFORMER_RADIUS)
        self.InitAttr(op, float, c4d.PY_SPHERE_DEFORMER_STRENGTH)

        if not isCloneInit:
            op[c4d.PY_SPHERE_DEFORMER_RADIUS] = 200.0
            op[c4d.PY_SPHERE_DEFORMER_STRENGTH] = 0.5

        return True

    def Message(self, node, msgId, data):
        """Called by Cinema 4D part to notify the object to a special event.

        Args:
            node (c4d.BaseObject): The instance of the ObjectData.
            msgId (int): The message ID type.
            data (Any): The message data, the type depends of the message passed.

        Returns:
            Depends of the message type, most of the time True.
        """
        # Enables deform tick when the object is created from the UI.
        if msgId == c4d.MSG_MENUPREPARE:
            node.SetDeformMode(True)

        return True

    def ModifyObject(self, mod, doc, op, op_mg, mod_mg, lod, flags, thread):
        """Called by Cinema 4D with the object to modify.

        Args:
            mod (c4d.BaseObject): The Python Modifier.
            doc (c4d.documents.BaseDocument): The document containing the plugin object.
            op (c4d.BaseObject): The object to modify.
            op_mg (c4d.Matrix): The object's world matrix.
            mod_mg (c4d.Matrix): The modifier object's world matrix.
            lod (float): The level of detail.
            flags (int): Currently unused.
            thread (c4d.threading.BaseThread): The calling thread.

        Returns:
            True if the object was modified, otherwise False.
        """
        # Modifies the point object
        if not op.CheckType(c4d.Opoint):
            return True

        # Retrieves points
        points = op.GetAllPoints()

        # If there is no point, nothing to modify we leave
        if len(points) == 0:
            return True

        # Retrieves parameters
        radius = mod[c4d.PY_SPHERE_DEFORMER_RADIUS]
        strength = mod[c4d.PY_SPHERE_DEFORMER_STRENGTH]

        # Calculates a weight map, so weight map can drive the deformer
        weights = op.CalcVertexmap(mod)

        # Calculate the deformation
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

            # Calculates the point position
            finalPoint = finalStrength * ((finalPoint.GetNormalized()) * radius) + (1.0 - finalStrength) * finalPoint

            # Defines the points position
            op.SetPoint(index, finalPoint * invMatrix)

        # Updates input object
        op.Message(c4d.MSG_UPDATE)

        return True

    def GetDimension(self, op, mp, rad):
        """Called By Cinema to retrieve the bounding box of the generated object (BaseObject.GetRad()).

        Args:
            op (c4d.BaseObject): The instance of the ObjectData.
            mp (c4d.Vector): Assign the center point of the bounding box to this vector.
            rad (c4d.Vector): Assign the XYZ bounding box radius to this vector.
        """
        value = op[c4d.PY_SPHERE_DEFORMER_RADIUS]
        if value is None:
            return

        mp = c4d.Vector()
        rad = c4d.Vector(value)

    def GetHandleCount(self, op):
        """Called to get the number of handles the object has. Part of the automated handle interface.

        Args:
            op (c4d.BaseObject): The instance of the ObjectData.

        Returns:
            int: The number of handles for the object.
        """
        return SpherifyModifier.HANDLECOUNT

    def GetHandle(self, op, i, info):
        """Called by Cinema 4D to retrieve the information of a given handle ID to represent a/some parameter(s).

        Args:
            op (c4d.BaseObject): The instance of the ObjectData.
            i (int): The handle index.
            info (c4d.HandleInfo): The HandleInfo to fill with data.
        """
        # Retrieves parameters value from the generator object
        rad = op[c4d.PY_SPHERE_DEFORMER_RADIUS] if op[c4d.PY_SPHERE_DEFORMER_RADIUS] is not None else 200.0
        strength = op[c4d.PY_SPHERE_DEFORMER_STRENGTH] if op[c4d.PY_SPHERE_DEFORMER_STRENGTH] is not None else 0.5

        # According the HandleID we are asked , defines different position/direction.
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

    def SetHandle(self, op, i, p, info):
        """Called by Cinema 4D when the user set the handle.

        This is the place to retrieve the information of a given handle ID and drive your parameter(s).

        Args:
            op (c4d.BaseObject): The instance of the ObjectData.
            i (int): The handle index.
            p (c4d.Vector): The new Handle Position.
            info (c4d.HandleInfo): The HandleInfo filled with data.
        """
        val = p.x
        if i == 0:
            # Radius handle
            op[c4d.PY_SPHERE_DEFORMER_RADIUS] = val

        elif i == 1:
            # Strength handle
            op[c4d.PY_SPHERE_DEFORMER_STRENGTH] = c4d.utils.ClampValue(val * 0.001, 0.0, 1.0)


    def Draw(self, op, drawpass, bd, bh):
        """Called by Cinema 4D when the display is updated to display some visual element of your object in the 3D view.

        This is also the place to draw handles.

        Args:
            op (c4d.BaseObject): The instance of the ObjectData.
            bd (c4d.BaseDraw): The editor's view.
            bh (c4d.plugins.BaseDrawHelp): The BaseDrawHelp editor's view.

        Returns:
            The result of the drawing (most likely c4d.DRAWRESULT_OK)
        """
        # If the current draw pass is for object drawing (polygon spline, etc)
        if drawpass == c4d.DRAWPASS_OBJECT:

            # Retrieves the object color
            bd.SetPen(bd.GetObjectColor(bh, op), c4d.SET_PEN_USE_PROFILE_COLOR)
            bd.SetMatrix_Matrix(None, c4d.Matrix())

            # Defines the scale/rotation where drawing will operate by the radius of the generator
            rad = op[c4d.PY_SPHERE_DEFORMER_RADIUS]
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

        # If the current draw pass is for handle drawing
        elif drawpass == c4d.DRAWPASS_HANDLES:
            # Resets the matrix
            bd.SetMatrix_Matrix(None, bh.GetMg())

            # Checks if one of the handle of the current object is currently hovered by the mouse.
            hitId = op.GetHighlightHandle(bd)

            for i in range(SpherifyModifier.HANDLECOUNT):
                # Defines the color of the handle according of the hovered state of the object.
                hoverColor = c4d.VIEWCOLOR_ACTIVEPOINT if hitId != i else c4d.VIEWCOLOR_SELECTION_PREVIEW
                bd.SetPen(c4d.GetViewColor(hoverColor), 0)

                # Retrieves the information of the current handle.
                info = c4d.HandleInfo()
                self.GetHandle(op, i, info)

                # Draws the handle to the correct position
                bd.DrawHandle(info.position, c4d.DRAWHANDLE_BIG, 0)

            # Draw the line to the second Handle
            bd.SetPen(c4d.GetViewColor(c4d.VIEWCOLOR_ACTIVEPOINT), 0)
            bd.DrawLine(info.position, c4d.Vector(0), 0)

        # If the current draw pass is not the object or handle, skip this Draw Call.
        else:
            return c4d.DRAWRESULT_SKIP

        return c4d.DRAWRESULT_OK


if __name__ == "__main__":
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "opyspheredeformer.tif")
    if not os.path.isfile(fn):
        raise FileNotFoundError(f"Icon file not found at path: {fn}")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    # Registers the object plugin
    c4d.plugins.RegisterObjectPlugin(id=PLUGIN_ID,
                                 str="Py-Sphere Deformer",
                                 g=SpherifyModifier,
                                 description="opyspheredeformer",
                                 icon=bmp,
                                 # This flag must be passed, otherwise the deformer won't be able 
                                 # to modify the input object.
                                 info=c4d.OBJECT_MODIFIER)
