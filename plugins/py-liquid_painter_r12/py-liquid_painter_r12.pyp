"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam

Description:
    - Tool, Creates a liquid Painter Tool.
    - Consists of Metaball and Sphere.

Class/method highlighted:
    - c4d.plugins.ToolData
    - ToolData.GetState()
    - ToolData.MouseInput()
    - ToolData.Draw()
    - ToolData.GetCursorInfo()
    - ToolData.AllocSubDialog()

Compatible:
    - Win / Mac
    - R12, R13, R14, R15, R16, R17, R18, R19, R20, R21
"""
import c4d
import os

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1025247

# Values must match with the header file, usd by c4d.plugins.GeLoadString
IDS_PRIMITIVETOOL = 50000


class SettingsDialog(c4d.gui.SubDialog):
    """
    Dialog to display option in the ToolData, in this case the Sphere size.
    """
    parameters = {}

    def __init__(self, arg):
        # Checks if the argument passed is a dictionary
        if not isinstance(arg, dict):
            raise TypeError("arg is not a dict.")

        self.parameters = arg

    def CreateLayout(self):
        """
        This Method is called automatically when Cinema 4D Create the Layout (display) of the GeDialog.
        """
        value = getattr(self.parameters, "sphere_size", 15)

        # Creates a Group to align 2 items
        if self.GroupBegin(id=1000, flags=c4d.BFH_SCALEFIT, cols=2, rows=1):
            self.GroupBorderSpace(10, 10, 10, 10)

            # Creates a Static text and a number input
            self.AddStaticText(id=1001, flags=c4d.BFH_MASK, initw=120, name="Sphere Size", borderstyle=c4d.BORDER_NONE)
            self.AddEditNumberArrows(id=1002, flags=c4d.BFH_MASK)

            # Defines the default values
            self.SetFloat(id=1002, value=value, min=0, max=20)
        self.GroupEnd()
        return True

    def Command(self, messageId, msg):
        """
          This Method is called automatically when the user clicks on a gadget and/or changes its value this function will be called.
          It is also called when a string menu item is selected.
         :param messageId: The ID of the gadget that triggered the event.
         :type messageId: int
         :param bc: The original message container
         :type bc: c4d.BaseContainer
         :return: False if there was an error, otherwise True.
         """
        # When the user change the Gadget with the ID 1002 (the input number field)
        if id == 1002:
            # Stores the value in the parameter variable
            self.parameters['sphere_size'] = self.GetFloat(1002)
        
        return True


class LiquidTool(c4d.plugins.ToolData):
    """Inherit from ToolData to create your own tool"""

    def __init__(self):
        self.data = {'sphere_size':15}

    def GetState(self, doc):
        """
        Called by Cinema 4D to know if the tool can be used currently
        :param doc: The current active document.
        :type doc: c4d.documents.BaseDocument
        :return: True if the tool can be used, otherwise False.
        """
        if doc.GetMode() == c4d.Mpaint:
            return False

        return c4d.CMD_ENABLED

    def MouseInput(self, doc, data, bd, win, msg):
        """
        Called by Cinema 4D, when the user click on the viewport and the tool is active.
        Mainly the place to do moue interaction from the viewport.
        :param doc: The current active document.
        :type doc: c4d.documents.BaseDocument
        :param data:  The tool settings container.
        :type data: c4d.BaseContainer
        :param bd:  The BaseDraw object of the active editor view.
        :type bd: c4d.BaseDraw
        :param win: The EditorWindow object for the active editor view.
        :type win: c4d.gui.EditorWindow
        :param msg: The original message container.
        :type msg: c4d.BaseContainer
        :return: False if a problem occurred during this function.
        """
        # Retrieves which clicks is currently clicked
        device = 0
        if msg[c4d.BFM_INPUT_CHANNEL ]== c4d.BFM_INPUT_MOUSELEFT:
            device = c4d.KEY_MLEFT
        elif msg[c4d.BFM_INPUT_CHANNEL] == c4d.BFM_INPUT_MOUSERIGHT:
             device = c4d.KEY_MRIGHT
        else:
            return True

        # Creates a MetaBall object
        metaball = c4d.BaseObject(c4d.Ometaball)
        if metaball is None:
            raise MemoryError("Failed to create a Metaball.")

        # Defines some settings and create a Phong Tag
        metaball[c4d.METABALLOBJECT_SUBEDITOR] = 10
        pTag = metaball.MakeTag(c4d.Tphong)
        if pTag is None:
            raise MemoryError("Failed to create a Phong Tag.")

        # Adds an undo step
        doc.AddUndo(c4d.UNDO_NEW, metaball)

        # Inserts the object in the active document and set it as active one.
        doc.InsertObject(metaball)
        doc.SetActiveObject(metaball)

        # Updates the Viewport (so the metaball is drawn)
        c4d.DrawViews(c4d.DA_ONLY_ACTIVE_VIEW | c4d.DA_NO_THREAD | c4d.DA_NO_ANIMATION)

        # Retrieves the X/Y screen position of the mouse.
        mx = msg[c4d.BFM_INPUT_X]
        my = msg[c4d.BFM_INPUT_Y]

        # Start a Dragging session
        win.MouseDragStart(button=device, mx=int(mx), my=int(my), flags=c4d.MOUSEDRAGFLAGS_DONTHIDEMOUSE|c4d.MOUSEDRAGFLAGS_NOMOVE)
        result, dx, dy, channel = win.MouseDrag()

        # While the Mouse is still in the Dragging (clicked) state
        while result == c4d.MOUSEDRAGRESULT_CONTINUE:
            # If user doesnt move the mouse simply updates frag information
            if dx == 0.0 and dy == 0.0:
                result, dx, dy, channel = win.MouseDrag()
                continue

            # Offsets the original position with the delta of the dragging
            mx += dx
            my += dy

            # Creates a Sphere
            sphere = c4d.BaseObject(c4d.Osphere)
            if sphere is None:
                raise MemoryError("Failed to create a Sphere.")

            # Defines the position of the sphere from Screen Space to World Space
            sphere.SetAbsPos(bd.SW(c4d.Vector(mx, my, 500.0)))

            # Defines the sphere radius
            sphere[c4d.PRIM_SPHERE_RAD] = self.data["sphere_size"]

            # Inserts it under the metaball
            sphere.InsertUnder(metaball)

            # Updates the Viewport (so the metaball with the newly created sphere is drawn)
            c4d.DrawViews(c4d.DA_ONLY_ACTIVE_VIEW | c4d.DA_NO_THREAD | c4d.DA_NO_ANIMATION)

            # Updates drag information
            result, dx, dy, channel = win.MouseDrag()

        # If the user press ESC while dragging, do an Undo (remove the Metaball Object)
        if win.MouseDragEnd() == c4d.MOUSEDRAGRESULT_ESCAPE:
            doc.DoUndo(True)

        # Pushes an update event to Cinema 4D
        c4d.EventAdd()
        return True

    def Draw(self, doc, data, bd, bh, bt, flags):
        """
        Called by Cinema 4d when the display is updated to display some visual element of your tool in the 3D view.
        :param doc: The current active document.
        :type doc: c4d.documents.BaseDocument
        :param data: The tool settings container.
        :type data: c4d.BaseContainer.
        :param bd: The editor's view.
        :type bd: c4d.BaseDraw
        :param bh: The BaseDrawHelp editor's view.
        :type bh: c4d.plugins.BaseDrawHelp
        :param bt: The calling thread.
        :type bt: c4d.threading.BaseThread
        :param flags: The current drawing pass.
        :type flags: TOOLDRAWFLAGS
        :return: The result of the drawing (most likely c4d.DRAWRESULT_OK)
        """

        # Resets the drawing matrix to the world space matrix.
        bd.SetMatrix_Matrix(None, c4d.Matrix())

        # If the DrawPass is the Highlight one
        if flags & c4d.TOOLDRAWFLAGS_HIGHLIGHT:
            p = [c4d.Vector(), c4d.Vector(100, 0, 0), c4d.Vector(50, 100, 0)]
            f = [c4d.Vector(1, 0, 0), c4d.Vector(1, 0, 0), c4d.Vector(1, 0, 0)]

        # If the DrawPass asks the inverse Z (ignore it, for 2D drawing)
        elif flags & c4d.TOOLDRAWFLAGS_INVERSE_Z:
            p = [c4d.Vector(), c4d.Vector(100, 0, 0), c4d.Vector(50, -100, 0)]
            f = [c4d.Vector(0, 0, 1), c4d.Vector(0, 0, 1), c4d.Vector(0, 0, 1)]

        # In any other cases
        else:
            p = [c4d.Vector(), c4d.Vector(-100, 0, 0), c4d.Vector(-50, 100, 0)]
            f = [c4d.Vector(0, 1, 0), c4d.Vector(0, 1, 0), c4d.Vector(0, 1, 0)]

        # Draw the polygon
        bd.DrawPolygon(p, f)
        return c4d.TOOLDRAW_HANDLES | c4d.TOOLDRAW_AXIS

    def GetCursorInfo(self, doc, data, bd, x, y, bc):
        """
        Called by Cinema 4D when the cursor is over editor window to get the state of the mouse pointer.
        :param doc: The current active document.
        :type doc: c4d.documents.BaseDocument
        :param data: The tool settings container.
        :type data: c4d.BaseContainer
        :param bd: The editor's view.
        :type bd: c4d.BaseDraw
        :param x: The x coordinate of the mouse cursor relative to the top-left of the currently active editor view.
        :type x: float
        :param y:The y coordinate of the mouse cursor relative to the top-left of the currently active editor view.
        :type y: float
        :param bc: The container to store the result in.
        :type bc: c4d.BaseContainer
        :return:
        """
        # If the cursor has left a user area, simply return True
        if bc.GetId() == c4d.BFM_CURSORINFO_REMOVE:
            return True

        # Sets the BubbleHelp string and cursor.
        bc.SetString(c4d.RESULT_BUBBLEHELP, c4d.plugins.GeLoadString(IDS_PRIMITIVETOOL))
        bc.SetInt32(c4d.RESULT_CURSOR, c4d.MOUSE_POINT_HAND)
        return True

    def AllocSubDialog(self, bc):
        """
        Called by Cinema 4D To allocate the Tool Dialog Option.
        :param bc: Currently not used.
        :type bc: c4d.BaseContainer
        :return: The allocated sub dialog.
        """
        return SettingsDialog(getattr(self, "data", {'sphere_size': 15}))


if __name__ == "__main__":
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "liquid.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    # Registers the tool plugin
    c4d.plugins.RegisterToolPlugin(id=PLUGIN_ID,
                                   str="Py-Liquid Painter",
                                   info=0, icon=bmp,
                                   help="This string is shown in the statusbar",
                                   dat=LiquidTool())
