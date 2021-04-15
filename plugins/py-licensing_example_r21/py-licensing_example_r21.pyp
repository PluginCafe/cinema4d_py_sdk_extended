"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Demonstrates how a plugin can implements a custom licensing in Python.
    - Opens a dialog which asks for the serial of the user, according to the current user_id logged in.
    - Saves a fie in the temp folder if the serial is correct so the next startup doesn't ask the serial again.

Class/method highlighted:
    - c4d.ExportLicenses()
    - c4d.gui.GeDialog
    - GeDialog.CreateLayout()
    - GeDialog.InitValues()
    - GeDialog.Command()

Note:
    Keep in mind python is a scripted language, meaning there is no 100% way to secure it.
    At a given time the script will be in the memory.

    Please don't implement security/serial checking logic into your plugin, instead, it's preferred to send
    the data into a server which will check for the validity of the entered serial.

    But due to the nature of python, it will still be more or less easy to bypass any kind of security
    and directly register the plugin by editing a plugin source code.

    Even if you encrypt your python plugin it will be just harder for the attackers but not impossible.
"""
import c4d
import os
import errno
import json
import sys


class LicenceHelper(object):

    def __init__(self):
        data = json.loads(c4d.ExportLicenses())

        # The Cinema product configuration that was running when the report was generated
        self.productID = data.get("currentproduct")

        # A unique identifier directly bound to the hardware used when the license report was generated;
        # the id stays constant as long as potential changes to hardware configuration are limited
        self.systemID = data.get("systemid")

        # A unique identifier directly bound to the user account used to login in id.maxon.net
        self.userID = data.get("userid")

        # The Customer surname bound to the user ID
        self.surname = data.get("surname")

        # The Customer name bound to the user ID
        self.name = data.get("name")

        # The path where the license will be saved (to avoid to bother the user and ask its serial, each startup)
        tempFolder = c4d.storage.GeGetC4DPath(c4d.C4D_PATH_STARTUPWRITE)
        self.storedLicensePath = os.path.join(tempFolder, "plugins", "py_licensing_example", "license.txt")

    def IsValidSerial(self, enteredLicense):
        """Very stupid check if the entered serial is valid.
        
        This is the place where you should hook your licensing logic.

        Args:
            enteredLicense (str): The string entered as serial.

        Returns:
            bool: True if the serial is correct, False otherwise.
        """
        return enteredLicense == self._GetValidSerial()

    def _GetValidSerial(self):
        return "License_{0}".format(self.userID)

    def SaveSerialInFile(self):
        """To be called in order to save the serial somewhere in the client,
        so we don't ask each restart for the serial
        """
        # Creates the directory if it does not exist
        parentDirLicFile = os.path.dirname(self.storedLicensePath)
        try:
            os.makedirs(parentDirLicFile)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(parentDirLicFile):
                pass
            else:
                raise

        # Writes the data into the license file
        with open(self.storedLicensePath, "w") as licFile:
            licFile.write(self._GetValidSerial())

    def IsStoredSerialValid(self):
        """Called to read if there is already a file saved (i.e. the user already entered a valid serial and was saved)."""
        # Checks if the file exists
        if not os.path.exists(self.storedLicensePath):
            return False

        # Reads the content
        licFileContent = None
        with open(self.storedLicensePath, "r", encoding="utf-8") as licFile:
            licFileContent = licFile.read()

        # Checks the license
        return self.IsValidSerial(licFileContent)


class LicensingExampleDialog(c4d.gui.GeDialog, LicenceHelper):

    ID_EDIT_TEXT    = 10000
    ID_STATUS_TEXT  = 10001
    serialEnteredIsValid = False

    def CreateLayout(self):
        """This Method is called automatically when Cinema 4D Create the Layout (display) of the Dialog."""
        # Defines the title of the Dialog
        self.SetTitle("Licensing Example -- Ask for serial")

        # Defines some helper text
        self.AddStaticText(self.ID_STATUS_TEXT, c4d.BFH_LEFT | c4d.BFV_CENTER,
                           name="Serial is not valid, the correct one is {}".format(self._GetValidSerial()))

        # Defines an edit text, where the user will enter his serial
        self.AddEditText(self.ID_EDIT_TEXT, c4d.BFH_SCALEFIT | c4d.BFV_TOP, editflags=c4d.EDITTEXT_HELPTEXT)

        # Adds a ok Button
        self.AddDlgGroup(c4d.DLG_OK)

        return True

    def InitValues(self):
        """This method is called automatically after the GUI is initialized."""
        # Defines the help text present in the Edit Text
        self.SetString(self.ID_EDIT_TEXT,
                       "Enter the correct serial here",
                       flags=c4d.EDITTEXT_HELPTEXT)

        return True

    def Command(self, messageId, bc):
        """This Method is called automatically when the user clicks on a gadget and/or changes its value this function will be called.

        It is also called when a string menu item is selected.

        Args:
            messageId (int): The ID of the gadget that triggered the event.
            bc (c4d.BaseContainer): The original message container

        Returns:
            False if there was an error, otherwise True.
        """
        # User enter something in the input text
        if messageId == self.ID_EDIT_TEXT:
            # Retrieves teh text from the input string field and converts it to utf-8
            enteredString = self.GetString(self.ID_EDIT_TEXT)

            # Checks if the entered string is a correct serial
            if self.IsValidSerial(enteredString):

                # If the serial is correct, update the text and define the variable serialEnteredIsValid
                # so its possible to know the value outside of the dlg, see main.
                self.SetString(self.ID_STATUS_TEXT, "Serial is valid")
                self.serialEnteredIsValid = True

            else:
                # If serial is not valid, update the text and also define the status of the verification.
                self.SetString(self.ID_STATUS_TEXT, "Serial is not valid, the correct one is {}".format(self._GetValidSerial()))
                self.serialEnteredIsValid = False
            return True

        # User click on Ok Button
        elif messageId == c4d.DLG_OK:
            # Close the dialog
            self.Close()

        return True


def RegisterPlugin():
    """Registers your plugin(s) here e.g. RegisterCommandPlugin."""
    print("Register your plugin here")


if __name__ == "__main__":
    # If there is nogui argument(commandline or c4dpy) don't run this plugin since it open a dialog.
    if "-nogui" in sys.argv:
        exit()

    # Creates a new instance of the GeDialog
    dlg = LicensingExampleDialog()

    # Checks if there is already an existing serial
    if dlg.IsStoredSerialValid():
        # If there is already an existing license that is correct, register our plugin and leave.
        RegisterPlugin()
        exit()

    # Opens the GeDialog to ask the serial to the user,
    # Since it opens it as Modal, it blocks Cinema 4D.
    dlg.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE, defaultw=300, defaulth=50)

    # Checks if the user entered a valid serial
    if dlg.serialEnteredIsValid:
        # Saves license somewhere in the disk so at next startup the user will not need to enter his serial again.
        dlg.SaveSerialInFile()

        # Registers the plugin.
        RegisterPlugin()
    else:
        print("No license found for license_example.pyp")
