"""
Copyright: MAXON Computer GmbH
Author: Manuel MAGALHAES, Maxime Adam

Description:
    - Creates a ToolData with a linkBox on it where it's possible to drag and drop an object.
    - When this linked object is clicked, its cloned and added to the document in a random position.

Class/method highlighted:
    - c4d.plugins.ToolData
    - ToolData.GetState()
    - ToolData.MouseInput()
    - ToolData.AllocSubDialog()
    - ToolData.Message()
    - c4d.gui.SubDialog
    - SubDialog.CreateLayout()
    - SubDialog.InitValues()
    - SubDialog.Command()

"""
import c4d
import random

# Be sure to use a unique ID obtained from https://plugincafe.maxon.net/c4dpluginid_cp
TOOLDATA_UI_PLUGIN_ID = 1054512

ID_CUSTOM_LINK = 1000
ID_BUTTON_APPLY = 1001
ID_BUTTON_RESET = 1002


class ToolDemoDialog(c4d.gui.SubDialog):
    """Creates a Dialog to show the ToolData options.

    This dialog will be displayed in the Attribute Manager so this means the ToolDemoDialog
    will be instantiate each time the tool is activate and destruct when the AM change its mode.
    """
    def __init__(self, sharedDict):
        super(ToolDemoDialog, self).__init__()

        # Checks if the argument passed is a dictionary
        if not isinstance(sharedDict, dict):
            raise TypeError("sharedDict is not a dict.")

        # Since its a dictionary it will not be a copy of the initial dict, but a reference of it.
        # This means if we change the data in the SubDialog it will also change it in the tool data and vise versa.
        self.sharedDict = sharedDict

        # This variable will store the LinkBox custom gui defined in CreateLayout.
        self.linkGadget = None

    def CreateLayout(self):
        """This Method is called automatically when Cinema 4D Create the Layout (display) of the Dialog."""
        if self.GroupBegin(0, c4d.BFH_SCALEFIT, 1, 0, ""):
            if self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 0, ""):
                self.AddStaticText(0, c4d.BFH_RIGHT, 0, 12, "Object:", c4d.BORDER_WITH_TITLE_BOLD)
                # Adds a BaseContainer so the linkBox will only accept sphere and cube as dropped objects.
                bc = c4d.BaseContainer()
                accept = c4d.BaseContainer()
                accept.SetInt32(c4d.Ocube, 1)
                accept.SetInt32(c4d.Osphere, 1)
                bc.SetContainer(c4d.DESC_ACCEPT, accept)
                self.linkGadget = self.AddCustomGui(ID_CUSTOM_LINK, c4d.CUSTOMGUI_LINKBOX, "", c4d.BFH_LEFT, 240, 12, bc)
            self.GroupEnd()

            # Adds some buttons
            if self.GroupBegin(0, c4d.BFH_SCALEFIT, 3, 0, ""):
                self.AddButton(ID_BUTTON_APPLY, c4d.BFH_LEFT, c4d.gui.SizePix(50), c4d.gui.SizePix(10), "Apply")
                self.AddButton(ID_BUTTON_RESET, c4d.BFH_LEFT, c4d.gui.SizePix(50), c4d.gui.SizePix(10), "Reset")
            self.GroupEnd()
        self.GroupEnd()
        return True
    
    def InitValues(self):
        """This Method is called automatically after the GUI is initialized."""
        # This is important to init the LinkBox gadget with the link stored in the tool data.
        # Otherwise, the link will be erase when the ui is refreshed.
        self.linkGadget.SetLink(self.sharedDict['link'])
        return True
        
    def Command(self, commandID, msg):
        """This Method is called automatically when the user clicks on a gadget and/or changes its value this function will be called.

        It is also called when a string menu item is selected.

        Args:
            commandID (int): The ID of the gadget that triggered the event.
            msg (c4d.BaseContainer): The original message container

        Returns:
            bool: False if there was an error, otherwise True.
        """
        # If the user interact with the LinkBox
        if commandID == ID_CUSTOM_LINK:
            # Retrieves the data from the LinkBox
            obj, objName, objID = self.GetDataFromLinkBox()

            # Stores them in the shared dict
            self.sharedDict['link'] = obj
            self.sharedDict['linkGUID'] = objID

        # If the user press the Apply Button we send a Message to the tool to inform to perform an action
        elif commandID == ID_BUTTON_APPLY:
            if self.sharedDict['link'] is None:
                c4d.gui.MessageDialog("No object is currently defined.")
                return True

            # Retrieve the c4d.plugins.BasePlugin corresponding to our ToolData.
            # Of course we could have stored our instance of ToolData in the shared dict.
            tool = c4d.plugins.FindPlugin(TOOLDATA_UI_PLUGIN_ID, c4d.PLUGINTYPE_TOOL)
            if tool is None:
                raise RuntimeError("Unable to find the registered tool.")

            # Sends a message to the ToolData with a unique ID
            # Ideally a new plugin should be used so the ToolData plugin ID and the Message Plugin ID is very distinct.
            # In the end it does not matter, you could use whatever kind of message you want such as MSG_BASECONTAINER.
            tool.Message(TOOLDATA_UI_PLUGIN_ID)

        # If the user press the Reset Button
        elif commandID == ID_BUTTON_RESET:
            # Resets the data and the UI.
            self.linkGadget.SetLink(None)
            self.sharedDict["link"] = None
            self.sharedDict["linkGUID"] = None

        return True

    def GetDataFromLinkBox(self):
        """Retrieves the object linked on the linkBox, its name, and its GUID

        Returns:
            tuple(c4d.BaseObject, str, int): A tuple with the linked object, the object's Name and the object's GUID.
        """
        # Retrieves the gadget added in CreateLayout
        if self.linkGadget is None:
            raise RuntimeError("couldn't retrieve the linkBox gadget")

        # Retrieves the object linked
        linkedObject = self.linkGadget.GetLink()
        if linkedObject is None:
            return None, None, None
        
        # Retrieves object's information.
        objName = linkedObject.GetName()
        objGUID = linkedObject.GetGUID()
        return linkedObject, objName, objGUID


class ToolDataWithUiExample(c4d.plugins.ToolData):
    """Inherit from ToolData to create your own tool"""

    def __init__(self):
        # This dictionary will be passed to the SubDialog. This will let us storing persistent data
        # This means if yo change the data in the SubDialog it will also change it in the tool data and vise versa.
        self.sharedDict = {'link': None, 'linkGUID': None}

    def GetState(self, doc):
        """Called by Cinema 4D to know if the tool can be used currently

        Args:
            doc (c4d.documents.BaseDocument): The current active document.

        Returns:
            c4d.CMD_ENABLED to enable, or **False** to disable.
        """
        return c4d.CMD_ENABLED

    def Message(self, doc, data, msgType, t_data):
        """Called when the tool receives messages.

        Args:
            doc (c4d.documents.BaseDocument): The current document.
            data (c4d.BaseContainer): The message data.
            msgType (int): The Message type.
            t_data (Any): Depends on `type`.

        Returns:
            any: Depends on the message `type`.
        """
        # If we received a message with the plugin ID(since its a unique ID it come from us, see line 115)
        if msgType == TOOLDATA_UI_PLUGIN_ID:
            # Creates a clones with the linked object
            self.CreateAClone(self.sharedDict["link"], createUndo=True)

        return True

    def MouseInput(self, doc, data, bd, win, msg):
        """Called by Cinema 4D, when the user click on the viewport and the tool is active.

        The main place to do mouse interaction from the viewport.

        Args:
            doc (c4d.documents.BaseDocument): The current active document.
            data (c4d.BaseContainer): The tool settings container.
            bd (c4d.BaseDraw): The BaseDraw object of the active editor view.
            win (c4d.gui.EditorWindow): The EditorWindow object for the active editor view.
            msg (c4d.BaseContainer): The original message container.

        Returns:
            bool: False** if a problem occurred during this function.
        """
        # Leaves if its not the left mouse click that occurred
        if msg[c4d.BFM_INPUT_CHANNEL] != c4d.BFM_INPUT_MOUSELEFT:
            return True

        # Check if there's an object linked in the ui
        if self.sharedDict["link"] is None or not self.sharedDict["link"].IsAlive():
            return True

        # Creates a clones with the linked object.
        # Since we are in the MouseInput we don't need to call doc.StartUndo and doc.EndUndo.
        self.CreateAClone(self.sharedDict["link"], createUndo=False)

        return True
        
    def AllocSubDialog(self, bc):  
        """Called by Cinema 4D To allocate the Tool Dialog Option.

        Args:
            bc (c4d.BaseContainer): Currently not used.

        Returns:
            ToolDemoDialog: The allocated sub dialog.
        """
        return ToolDemoDialog(self.sharedDict)

    def CreateAClone(self, op, createUndo):
        """Creates a clone of the passed object and insert it in the document.

        Args:
            op (Union[c4d.BaseObject, None]): The object that must be cloned, if None nothing happens.
            createUndo (bool): True if the method should call StartUndo/EndUndo otherwise False.

        Returns:
            c4d.BaseObject: The cloned object already inserted.
        """
        if op is None:
            return

        doc = op.GetDocument()
        if doc is None:
            raise RuntimeError("The object is not into a document.")

        # Creates a clone of the linked Object    
        cloned = op.GetClone()
        if cloned is None:
            raise RuntimeError("Failed to copy the object.")

        if createUndo:
            doc.StartUndo()

        # Adds an undo step
        doc.AddUndo(c4d.UNDO_NEW, cloned)

        # Inserts the cloned object in the active document.
        doc.InsertObject(cloned)

        # Creates some random position
        x = round(random.uniform(-1000.0, 1000.0), 3)
        y = round(random.uniform(-1000.0, 1000.0), 3)
        z = round(random.uniform(-1000.0, 1000.0), 3)

        # Sets the position of the object
        newPos = c4d.Vector(x, y, z)
        cloned.SetRelPos(newPos)

        if createUndo:
            doc.EndUndo()

        # Pushes an update event to Cinema 4D
        c4d.EventAdd()


if __name__ == "__main__":
    c4d.plugins.RegisterToolPlugin(id=TOOLDATA_UI_PLUGIN_ID,
                                   str="ToolData With UI",
                                   info=0,
                                   icon=None,
                                   help="A Tool with a SubDialog UI",
                                   dat=ToolDataWithUiExample())
