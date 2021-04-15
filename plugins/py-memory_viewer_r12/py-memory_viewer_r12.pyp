"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam

Description:
    - Creates a Dialog which display the memory usage.
    - The Memory Usage is displayed in a custom Gadget (GeUserArea).

Note:
    - The menu bar is disable in the Dialog and the Dialog pin is manually added to support GeDialog docking.

Class/method highlighted:
    - c4d.gui.GeUserArea
    - GeUserArea.Init()
    - GeUserArea.DrawMsg()
    - c4d.gui.GeUserArea
    - GeUserArea.CreateLayout()
    - GeUserArea.InitValues()
    - GeUserArea.Timer()
    - c4d.plugins.CommandData
    - CommandData.Execute()
    - CommandData.RestoreLayout()

"""
import c4d
import collections
import os

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1025249


def CalcValueToMB(value):
    """Convert bit to mb

    Args:
        value (int): size in bit

    Returns:
        size in mb
    """
    return value / 1024.0 / 1024.0


class MemoryViewerUserArea(c4d.gui.GeUserArea):
    # collections.deque that will store all the datas
    values = None

    # Defines how many values the GeUserArea will display
    division = 40

    # Defines the range of the value
    value_max = 0
    value_min = 0

    # Defines color
    highlight_line = c4d.Vector(0, 0.6, 0)
    black = c4d.Vector(0)
    shadow_line = c4d.Vector(0.15)

    def Init(self):
        self.values = collections.deque([0, ] * self.division)
        self.Update()
        return True

    def DrawMsg(self, x1, y1, x2, y2, msg_ref):
        """This Method is called automatically when Cinema 4D Draw the Gadget.

        Args:
            x1 (int): The upper left x coordinate.
            y1 (int): The upper left y coordinate.
            x2 (int): The lower right x coordinate.
            y2 (int): The lower right y coordinate.
            msg_ref (c4d.BaseContainer): The original mesage container.
        """
        # Initializes draw region
        self.OffScreenOn()
        self.SetClippingRegion(x1, y1, x2, y2)
        self.DrawRectangle(x1, y1, x2, y2)

        # Draws the black background
        self.DrawSetPen(self.black)
        self.DrawRectangle(x1, y1, x2, y2)

        # Draws the background grid
        self.DrawSetPen(self.shadow_line)
        x_step = int((x2 - x1) / self.division + 1)
        y_step = int((y2 - y1) / self.division + 1)

        for i in range(int(self.division)):
            self.DrawLine(x_step * i, y2 - y1, x_step * i, y2 - y2)
            self.DrawLine(x1, y2 - (y_step * i), x2, y2 - (y_step * i))

        # Draws the graphic
        offset = 10
        self.DrawSetPen(self.highlight_line)

        # Iterates each points
        for i, v in enumerate(self.values):
            # Skips last point
            if i == len(self.values) - 1:
                continue

            # Retrieves position from current to next one
            l_x1 = int(i * x_step)
            l_y1 = int(c4d.utils.RangeMap(v, self.value_min, self.value_max, y1 + offset, y2 - offset, False))
            l_x2 = int((i + 1) * x_step)
            l_y2 = int(c4d.utils.RangeMap(self.values[i + 1], self.value_min + 10, self.value_max, y1 + offset, y2 - offset,False))

            # Draws the line
            self.DrawLine(l_x1, y2 - l_y1, l_x2, y2 - l_y2)

        # Draws statistics legend
        vmax = ("%.3f MB" % (CalcValueToMB(self.value_max)))
        vmin = ("%.3f MB" % (CalcValueToMB(self.value_min)))

        self.DrawSetTextCol(self.highlight_line, self.black)
        self.DrawText(vmax, 0, 0)
        self.DrawText(vmin, 0, y2 - self.DrawGetFontHeight())

        return

    def Update(self):
        """Updates the memory information, push them to the self.value.

        Returns:
            c4d.BaseContainer: The data that has been pushed
        """
        # Retrieves the memory usage
        bc = c4d.storage.GeGetMemoryStat()
        v = bc[c4d.C4D_MEMORY_STAT_MEMORY_INUSE]

        # Rotates each values, so if a value was id 1, its now id 0
        self.values.rotate(-1)

        # Updates the range of value min/max
        if v > self.value_max:
            self.value_max = v
        elif v < self.value_min:
            self.value_min = v

        # Assigns latest values to the Memory used
        self.values[self.division - 1] = v

        # Redraw the GeUserArea
        self.Redraw()
        return bc


class MemoryViewerDialog(c4d.gui.GeDialog):
    def __init__(self):
        self.mem_info = MemoryViewerUserArea()
        self.cur_mem_info = None

        # Disables Menu Bar
        self.AddGadget(c4d.DIALOG_NOMENUBAR, 0)

    def CreateLayout(self):
        """This Method is called automatically when Cinema 4D Create the Layout (display) of the Dialog."""
        # Defines the title with the Computer Name
        bc = c4d.GetMachineFeatures()
        self.SetTitle(bc[c4d.MACHINEINFO_COMPUTERNAME])

        # Adds the Windows Pin gadget so user can dock the Dialog
        if self.GroupBegin(id=0, flags=c4d.BFH_SCALEFIT, rows=1, title="", cols=2, groupflags=c4d.BORDER_GROUP_IN):
            self.AddGadget(c4d.DIALOG_PIN, 0)
            self.cur_mem_info = self.AddStaticText(id=0, initw=0, inith=0, name="", borderstyle=0, flags=c4d.BFH_SCALEFIT)
        self.GroupEnd()

        # Adds a separator
        self.AddSeparatorH(inith=0)

        # Adds the User Area
        if self.GroupBegin(id=0, flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, title="", rows=1, cols=1, groupflags=c4d.BORDER_GROUP_IN):
            self.GroupBorderSpace(5, 5, 5, 5)

            # Defines unique ID to User Area, otherwise the update process will fail.
            area = self.AddUserArea(id=1001, flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)

            # Attaches the User Area to the Gadget
            self.AttachUserArea(self.mem_info, area)
        self.GroupEnd()
        return True

    def InitValues(self):
        """Called after CreateLayout being called to define the values in the UI.
        
        Returns:
            True if successful, or False to signalize an error.
        """
        # Defines the timing for Timer message to be called
        self.SetTimer(500)
        return True

    def Timer(self, msg):
        """This method is called automatically by Cinema 4D according to the timer set with GeDialog.SetTimer method.

        Args:
            msg (c4d.BaseContainer): The timer message
        """
        # Retrieves the current memory information and display it
        bc = self.mem_info.Update()
        self.SetString(self.cur_mem_info, ("Current: %.3f MB" % (CalcValueToMB(bc[c4d.C4D_MEMORY_STAT_MEMORY_INUSE]))))


class MemoryViewerCommandData(c4d.plugins.CommandData):
    """Command Data class that holds the MemoryViewerDialog instance."""
    dialog = None

    def Execute(self, doc):
        """Called when the user Execute the command (CallCommand or a clicks on the Command from the plugin menu).

        Args:
            doc (c4d.documents.BaseDocument): the current active document

        Returns:
            True if the command success
        """
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = MemoryViewerDialog()

        # Opens the dialog
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaulth=400, defaultw=400)

    def RestoreLayout(self, sec_ref):
        """Used to restore an asynchronous dialog that has been placed in the users layout.

        Args:
            sec_ref (PyCObject): The data that needs to be passed to the dialog (almost no use of it).

        Returns:
            True if the restore success
        """
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = MemoryViewerDialog()

        # Restores the layout
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)


if __name__ == "__main__":
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "mviewer.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    # Registers the Command plugin
    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                      str="Py-MemoryViewer",
                                      help="Show the current mem usage of Cinema 4D.",
                                      info=0,
                                      dat=MemoryViewerCommandData(),
                                      icon=bmp)
