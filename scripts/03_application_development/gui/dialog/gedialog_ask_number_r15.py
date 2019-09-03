"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a Modal Dialog asking for an integer or a float.
    - Retrieves the entered value, once the user exit the Dialog.

Class/method highlighted:
    - c4d.gui.GeDialog
    - GeDialog.CreateLayout()
    - GeDialog.AskClose()
    - GeDialog.InitValues()
    - GeDialog.Command()

Compatible:
    - Win / Mac
    - R15, R16, R17, R18, R19, R20, R21
"""
import c4d

# Defines constants to know if the dialog ask an integer or a float
DLG_TYPE_FLOAT = 1
DLG_TYPE_INT = 2


class AskNumber(c4d.gui.GeDialog):
    ID_EDIT_NUMBER = 10000

    def __init__(self, dlgType=DLG_TYPE_FLOAT, value=0.0):
        # Checks the type that will be used in the dialog
        if dlgType != DLG_TYPE_FLOAT and dlgType != DLG_TYPE_INT:
            raise ValueError("dlgType is not DLG_TYPE_FLOAT or DLG_TYPE_INT.")

        if dlgType == DLG_TYPE_FLOAT:
            try:
                value = float(value)
            except ValueError:
                raise ValueError("value should be convertible to float if DLG_TYPE_FLOAT is passed.")

        if dlgType == DLG_TYPE_INT:
            try:
                value = int(value)
            except ValueError:
                raise ValueError("value should be convertible to int if DLG_TYPE_INT is passed.")

        self.dlgType = dlgType
        self.defaultValue = value

        # The value stored if the user press OK
        self.value = None

        # If the user presses the cancel button
        self.userCancel = False

    def AskClose(self):
        """
        This Method is called automatically when self.Close() is called or the user press the Close cross in top menu.
        """

        # Cancel close if it's not called from OK or Cancel Button
        if self.value is None and not self.userCancel:
            return True

        return False

    def CreateLayout(self):
        """
        This Method is called automatically when Cinema 4D Create the Layout (display) of the Dialog.
        """
        # Defines the title of the Dialog
        self.SetTitle("Enter a Number")

        # Starts a group to get 2 elements in the same row
        if self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=2):
            # Adds a text to describe the input
            self.AddStaticText(0, c4d.BFH_LEFT, name="Number:")

            # Adds an number fields (the type of the number is defined in InitValue with SetInt32 or SetFloat)
            self.AddEditNumberArrows(self.ID_EDIT_NUMBER, c4d.BFH_SCALEFIT)
        self.GroupEnd()

        # Adds two buttons, Ok and Cancel
        self.AddDlgGroup(c4d.DLG_OK | c4d.DLG_CANCEL)

        return True

    def InitValues(self):
        """
        This Method is called automatically after the GUI is initialized.
        """

        # If the dlg type is an int we define the input number to only accept integer
        if self.dlgType == DLG_TYPE_INT:
            self.SetInt32(self.ID_EDIT_NUMBER, int(self.defaultValue))

        # If the dlg type is a float we define the input number to accept float
        elif self.dlgType == DLG_TYPE_FLOAT:
            self.SetFloat(self.ID_EDIT_NUMBER, float(self.defaultValue), step=0.1)

        return True

    def Command(self, id, msg):
        """
        This Method is called automatically when the user clicks on a gadget and/or changes its value this function will be called.
        It is also called when a string menu item is selected.

        :param id: The ID of the gadget that triggered the event.
        :param msg: The original message container
        :return: False if there was an error, otherwise True.
        """

        # If the user right click on the input, means user want to reset
        if id == self.ID_EDIT_NUMBER and msg[c4d.BFM_ACTION_RESET]:
            if self.dlgType == DLG_TYPE_FLOAT:
                self.SetFloat(self.ID_EDIT_NUMBER, self.defaultValue)
            else:
                self.SetInt32(self.ID_EDIT_NUMBER, self.defaultValue)

        # If the user click on Ok button, retrieves the values from the input
        if id == c4d.DLG_OK:
            self.value = self.GetFloat(self.ID_EDIT_NUMBER)
            self.userCancel = False
            self.Close()

        # If the user click on cancel button, resets the value and defines userCancel
        elif id == c4d.DLG_CANCEL:
            self.value = None
            self.userCancel = True
            self.Close()

        return True


def main():
    # Initialize a AskNumber Dialog
    dlg = AskNumber(DLG_TYPE_FLOAT, 42.42)

    # Open the Dialog in modal mode
    dlg.Open(c4d.DLG_TYPE_MODAL)

    # This code will be executed only when the Dialog will be closed
    # Access member variable of the dlg check if the user pressed cancel
    if dlg.userCancel:
        print "User Press the Cancel Button"
        return

    # Retrieves the values stored in the member variable of the Dialog
    print "Value entered: {0}".format(dlg.value)


if __name__ == "__main__":
    main()