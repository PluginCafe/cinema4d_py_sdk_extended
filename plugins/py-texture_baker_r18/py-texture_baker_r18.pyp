"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam

Description:
    - Creates a Dialog to manage texture baking.
    - Bakes selected object diffuse to the uv and display the result in the Picture Viewer.

Class/method highlighted:
    - c4d.threading.C4DThread
    - C4DThread.Main()
    - c4d.gui.GeDialog
    - GeDialog.CreateLayout()
    - GeDialog.Command()
    - GeDialog.CoreMessage()
    - GeDialog.AskClose()
    - c4d.plugins.CommandData
    - CommandData.Execute()
    - CommandData.RestoreLayout()

"""
import c4d

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1037872


class TextureBakerThread(c4d.threading.C4DThread):
    """Cinema 4D Thread for the TextureBaker Command Plugin"""

    def __init__(self, doc, textags, texuvws, destuvws):
        """Initializes the Texture Baker thread.

        Args:
            doc (c4d.documents.BaseDocument): the document hosting the object.
            textags (c4d.TextureTag): List of the texture tag(s) to bake. Must be assigned to an object.
            texuvws (c4d.UVWTag): The UVW tag(s) to bake.
            destuvws (c4d.UVWTag): The destination UVW tag for the bake.
        """
        self.doc = doc
        self.textags = textags
        self.texuvws = texuvws
        self.destuvws = destuvws

        self.bakeDoc = None
        self.bakeData = None
        self.bakeBmp = c4d.bitmaps.MultipassBitmap(512, 512, c4d.COLORMODE_RGB)
        self.bakeError = c4d.BAKE_TEX_ERR_NONE

    def Begin(self):
        """Setups and starts the texture baking thread."""

        # Defines baking setting
        bakeData = c4d.BaseContainer()
        bakeData[c4d.BAKE_TEX_WIDTH] = 512
        bakeData[c4d.BAKE_TEX_HEIGHT] = 512
        bakeData[c4d.BAKE_TEX_PIXELBORDER] = 1
        bakeData[c4d.BAKE_TEX_CONTINUE_UV] = False
        bakeData[c4d.BAKE_TEX_SUPERSAMPLING] = 0
        bakeData[c4d.BAKE_TEX_FILL_COLOR] = c4d.Vector(1)
        bakeData[c4d.BAKE_TEX_USE_BUMP] = False
        bakeData[c4d.BAKE_TEX_USE_CAMERA_VECTOR] = False
        bakeData[c4d.BAKE_TEX_AUTO_SIZE] = False
        bakeData[c4d.BAKE_TEX_NO_GI] = False
        bakeData[c4d.BAKE_TEX_GENERATE_UNDO] = False
        bakeData[c4d.BAKE_TEX_PREVIEW] = False
        bakeData[c4d.BAKE_TEX_COLOR] = True
        bakeData[c4d.BAKE_TEX_UV_LEFT] = 0.0
        bakeData[c4d.BAKE_TEX_UV_RIGHT] = 1.0
        bakeData[c4d.BAKE_TEX_UV_TOP] = 0.0
        bakeData[c4d.BAKE_TEX_UV_BOTTOM] = 1.0
        # bakeData[c4d.BAKE_TEX_OPTIMAL_MAPPING] = c4d.BAKE_TEX_OPTIMAL_MAPPING_CUBIC

        self.bakeData = bakeData

        # Initializes bake process
        bakeInfo = c4d.utils.InitBakeTexture(self.doc, self.textags, self.texuvws, self.destuvws, 
                                             self.bakeData, self.Get())
        self.bakeDoc = bakeInfo[0]
        self.bakeError = bakeInfo[1]

        if self.bakeError != c4d.BAKE_TEX_ERR_NONE or self.bakeDoc is None:
            return False

        # Starts bake thread
        self.Start(c4d.THREADMODE_ASYNC, c4d.THREADPRIORITYEX_BELOW)

        return True

    def BakeTextureHook(self, info):
        # Texture Baker hook, currently not used
        # print info
        pass

    def Main(self):
        # Bake Texture Thread Main routine
        self.bakeError = c4d.utils.BakeTexture(self.bakeDoc, self.bakeData, self.bakeBmp, self.Get(), 
                                               self.BakeTextureHook)

        # Sends core message once baking has finished
        c4d.SpecialEventAdd(PLUGIN_ID)


class TextureBakerHelper(object):

    def EnableButtons(self, baking):
        """Defines the state of the button according of the baking process.

        Args:
            baking: Current baking state (True if baking occurs)
        """
        self.Enable(self.BUTTON_BAKE, not baking)
        self.Enable(self.BUTTON_ABORT, baking)

    def Bake(self):
        """Bake the active object to texture"""
        # Retrieves selected document
        doc = c4d.documents.GetActiveDocument()
        if doc is None:
            return

        # Retrieves selected objects
        obj = doc.GetActiveObject()
        if obj is None:
            self.SetString(self.infoText, "Bake Init Failed: Select one single object")
            return

        # Retrieves texture and UVW tags from the selected object
        uvwTag = obj.GetTag(c4d.Tuvw)
        if uvwTag is None:
            self.SetString(self.infoText, "Bake Init Failed: No uv tag found")
            return

        tags = obj.GetTags()
        textags, texuvws, destuvws = [], [], []
        for tag in tags:
            if tag.CheckType(c4d.Ttexture):
                textags.append(tag)
                texuvws.append(uvwTag)
                destuvws.append(uvwTag)

        if len(textags) == 0:
            self.SetString(self.infoText, "Bake Init Failed: No texture tag found")
            return

        # Initializes and start texture baker thread
        self.aborted = False
        self.textureBakerThread = TextureBakerThread(doc, textags, texuvws, destuvws)

        # Initializes the thread
        if not self.textureBakerThread.Begin():
            # In case of errors, notifies the user
            print("Bake Init Failed: Error " + str(self.textureBakerThread.bakeError))
            self.SetString(self.infoText, str("Bake Init Failed: Error " + str(self.textureBakerThread.bakeError)))

        # Sets Button enable states so cancel button can be pressed
        self.EnableButtons(True)
        self.SetString(self.infoText, "Baking")

    def Abort(self):
        """Cancels the baking progress"""
        # Checks if there is a baking process currently
        if self.textureBakerThread and self.textureBakerThread.IsRunning():
            self.aborted = True
            self.textureBakerThread.End()
            self.textureBakerThread = None


class TextureBakerDlg(c4d.gui.GeDialog, TextureBakerHelper):
    """Main dialog for the Texture Baker"""

    BUTTON_BAKE = 1000
    BUTTON_ABORT = 1001

    aborted = False
    textureBakerThread = None
    infoText = None

    def CreateLayout(self):
        """This Method is called automatically when Cinema 4D Create the Layout (display) of the Dialog."""
        # Defines the title
        self.SetTitle("Texture Baker")

        # Creates 2 buttons for Bake / Abort button
        if self.GroupBegin(id=0, flags=c4d.BFH_SCALEFIT, rows=1, title="", cols=2, groupflags=0):
            self.AddButton(id=self.BUTTON_BAKE, flags=c4d.BFH_LEFT, initw=100, inith=25, name="Bake")
            self.AddButton(id=self.BUTTON_ABORT, flags=c4d.BFH_LEFT, initw=100, inith=25, name="Abort")
        self.GroupEnd()

        # Creates a statics text for the status
        if self.GroupBegin(id=0, flags=c4d.BFH_SCALEFIT, rows=1, title="", cols=1, groupflags=0):
            self.infoText = self.AddStaticText(id=0, initw=0, inith=0, name="", borderstyle=0, flags=c4d.BFH_SCALEFIT)
        self.GroupEnd()

        # Sets Button enable states so only bake button can be pressed
        self.EnableButtons(False)

        return True

    def Command(self, id, msg):
        """This Method is called automatically when the user clicks on a gadget and/or changes its value this function will be called.
        It is also called when a string menu item is selected.

        Args:
            id (int): The ID of the gadget that triggered the event.
            msg (c4d.BaseContainer): The original message container

        Returns:
            bool: False if there was an error, otherwise True.
        """
        if id == self.BUTTON_BAKE:
            self.Bake()

        elif id == self.BUTTON_ABORT:
            self.Abort()

        return True

    def CoreMessage(self, id, msg):
        """This Method is called automatically when Core (Main) Message is received.

        Args:
            id (int): The ID of the gadget that triggered the event.
            msg (c4d.BaseContainer): The original message container

        Returns:
            bool: False if there was an error, otherwise True.
        """
        # Checks if texture baking has finished
        if id == PLUGIN_ID:
            # Sets Button enable states so only bake button can be pressed
            self.EnableButtons(False)

            # If not aborted, means the baking finished
            if not self.aborted:
                # Updates the information status
                self.SetString(self.infoText, str("Baking Finished"))

                # Retrieves the baked bitmap
                bmp = self.textureBakerThread.bakeBmp
                if bmp is None:
                    raise RuntimeError("Failed to retrieve the baked bitmap.")

                # Displays the bitmap
                c4d.bitmaps.ShowBitmap(bmp)

                # Removes the reference to the C4D Thread, so the memory used is free
                self.textureBakerThread = None
                return True
            else:
                # If baking is aborted, updates the information status
                self.SetString(self.infoText, str("Baking Aborted"))

            return True

        return c4d.gui.GeDialog.CoreMessage(self, id, msg)

    def AskClose(self):
        """This Method is called automatically when self.Close() is called or the user press the Close cross in top menu.

        Returns:
            bool: True if the Dialog shouldn't close, otherwise False.
        """
        # Aborts the baking process on dialog close
        self.Abort()
        return False


class TextureBakerData(c4d.plugins.CommandData):
    """Command Data class that holds the TextureBakerDlg instance."""
    dialog = None

    def Execute(self, doc):
        """Called when the user Execute the command (CallCommand or a clicks on the Command from the plugin menu)

        Args:
            doc (c4d.documents.BaseDocument): the current active document

        Returns:
            bool: True if the command success
        """
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = TextureBakerDlg()

        # Opens the dialog
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=250, defaulth=50)

    def RestoreLayout(self, sec_ref):
        """Used to restore an asynchronous dialog that has been placed in the users layout.

        Args:
            sec_ref (PyCObject): The data that needs to be passed to the dlg (almost no use of it).

        Returns:
            bool: True if the restore success
        """
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = TextureBakerDlg()

        # Restores the layout
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)


if __name__ == "__main__":
    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID, str="Py-TextureBaker",
                                  help="Py - Texture Baker", info=0,
                                  dat=TextureBakerData(), icon=None)
