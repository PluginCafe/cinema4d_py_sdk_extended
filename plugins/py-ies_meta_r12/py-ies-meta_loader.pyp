"""
Copyright: MAXON Computer GmbH
Author: Manuel MAGALHAES

Description:
    - Shows how to create a scene loader plugin. This example is the counterpart of the export
    plugin. To test it, the exported text file will be needed. 
    - Shows how to use the description files to present option to the user about how to import the
    file. This options will be displayed in a form of a GeDialog to the user, or in the preferences, 
    in the corresponding Import/Export section. If the function c4d.documents.LoadDocument is used 
    to load the file, the flag c4d.SCENEFILTER_DIALOGSALLOWED must be defined so that the option will
    be presented to the user.
    
Class/method highlighted:
    - c4d.plugins.SceneLoaderData
    - SceneLoaderData.Identify()
    - SceneLoaderData.Load()
"""

import c4d

# SceneLoader are registered earlier than Cinema 4D Resource parser.
# To have all the constant defined in fies_loader.h, you need to manually parse them
import os
import symbol_parser
symbol_parser.parse_and_export_in_caller(os.path.join(os.path.dirname(__file__), "res"))

PLUGIN_ID = 1059408


class ExampleDialog(c4d.gui.GeDialog):

    def CreateLayout(self):
        """
        This Method is called automatically when Cinema 4D creates the Layout of the Dialog.
        Returns:
            bool: False if there was an error, otherwise True.
        """
        # Defines the title of the Dialog
        self.SetTitle("This is an example Dialog")

        # Creates a Ok and Cancel Button
        self.AddDlgGroup(c4d.DLG_OK | c4d.DLG_CANCEL)

        return True

    def Command(self, messageId, bc):
        """
        This Method is called automatically when the user clicks on a gadget and/or changes 
        its value this function will be called. It is also called when a string menu item is selected.

        Args:
            messageId (int): The ID of the gadget that triggered the event.
            bc (c4d.BaseContainer): The original message container.

        Returns:
            bool: False if there was an error, otherwise True.
        """
        # User click on Ok buttonG
        if messageId == c4d.DLG_OK:
            print("User Click on Ok")
            return True

        # User click on Cancel button
        elif messageId == c4d.DLG_CANCEL:
            print("User Click on Cancel")

            # Close the Dialog
            self.Close()
            return True

        return True


class IESMetaLoader(c4d.plugins.SceneLoaderData):
    """IESMeta Loader"""
    dialog = None

    def Init(self, node):
        """
        Called when a new instance of this object is created. In this context, this allow to define
        the option by default for the SceneLoaderPlugin that will be displayed to the user.
        
        Returns:
            bool: False if there was an error, otherwise True.
        """
        # Define the default value for the parameters.
        self.InitAttr(node, bool, IES_IMPORT_PRINT_TO_CONSOLE)
        node[IES_IMPORT_PRINT_TO_CONSOLE] = True
        return True

    def Identify(self, node, name, probe, size):
        """
        Cinema 4D calls this function for every registered scene loader plugin. This function
        should return True only if this plugin can handle the file. The parameter 'probe' contain a 
        small part of the file, usually the 1024 first characters. This allow to check if the header 
        of the file starts as expected, validating the fact this file can be read by the load 
        function.
        Args:
            node (c4d.BaseList2D): The node object.
            name (str): The name of the loader.
            probe (memoryview): The start of a small chunk of data from the start of the file for 
            testing this file type. Usually the probe size is 1024 bytes. Never call the buffer 
            outside this method!
            size (int): The size of the chunk for testing this file type.
        Returns:
            bool: True if the SceneLoaderData can load this kind of files.
        """
        # Check if the last three character are equal to 'txt'
        if "txt" in name[-3:]:
            # Check if the txt file start with the correct header.
            if bytes(probe[0:17]).decode().upper() == "IES Meta Exporter".upper():
                return True
        return False

    def Load(self, node, name, doc, filterflags, error, bt):
        """
        Called by Cinema 4D to load the file. This method is only called if the identify function
        returned True. The parameter 'node' allows to retrieve the options the user defined for this
        import.

        Args:
            node (c4d.BaseList2D): The node object representing the exporter.
            name (str): The filename of the file to save.
            doc (c4d.documents.BaseDocument): The document that should be saved.
            filterflags (SCENEFILTER): Options for the exporter.
            error (None): Not supported.
            bt (c4d.threading.BaseThread): The calling thread.

        Returns:
            FILEERROR: Status of the import process.
        """
        dialogAllowed = bool(filterflags & c4d.SCENEFILTER_DIALOGSALLOWED)
        isMainThread = c4d.threading.GeIsMainThread()

        print("is main thread  {}".format(isMainThread))
        print("is dialog allowed? {}".format(dialogAllowed))
        # GUI operation are not allowed if they are not executed from the main thread, always check
        # if this is the main thread. Check also if the flag is set to SCENEFILTER_DIALOGSALLOWED to
        # sure dialog can be displayed.
        if isMainThread:
            if dialogAllowed:
                # Open a GeDialog
                if self.dialog is None:
                    self.dialog = ExampleDialog()
                self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC,
                                 pluginid=PLUGIN_ID,
                                 defaultw=400,
                                 defaulth=32
                                 )

                # Create and display a Popup Menu
                menu = c4d.BaseContainer()
                menu.InsData(1001, 'Item 1')
                menu.InsData(1002, 'Item 2')
                menu.InsData(0, '')  # Append separator
                c4d.gui.ShowPopupDialog(cd=None, bc=menu, x=c4d.MOUSEPOS, y=c4d.MOUSEPOS)
        
        # Display the content of the file if the user check the option in the import options.
        # Opens the file in read mode and print all the lines
        if node[IES_IMPORT_PRINT_TO_CONSOLE]:
            with open(name, "r") as f:
                for line in f:
                    print(line)
        return c4d.FILEERROR_NONE


if __name__ == '__main__':
    c4d.plugins.RegisterSceneLoaderPlugin(id=PLUGIN_ID,
                                          str="Py-IES Meta (*.txt)",
                                          info=0,
                                          g=IESMetaLoader,
                                          description="fies_loader",
                                          )
