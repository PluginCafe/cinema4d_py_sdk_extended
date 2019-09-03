"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a basic Modal Dialog.

Note:
    - Due to the lifetime of the variable, GeDialog must be created as Modal in a script.

Class/method highlighted:
    - c4d.gui.GeDialog
    - GeDialog.CreateLayout()
    - GeDialog.Command()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21
"""
import c4d


class ExampleDialog(c4d.gui.GeDialog):

    def CreateLayout(self):
        """
        This Method is called automatically when Cinema 4D Create the Layout (display) of the Dialog.
        """
        # Defines the title of the Dialog
        self.SetTitle("This is an example Dialog")

        # Creates a Ok and Cancel Button
        self.AddDlgGroup(c4d.DLG_OK | c4d.DLG_CANCEL)

        return True

    def Command(self, messageId, bc):
        """
        This Method is called automatically when the user clicks on a gadget and/or changes its value this function will be called.
        It is also called when a string menu item is selected.

        :param messageId: The ID of the gadget that triggered the event.
        :param bc: The original message container
        :return: False if there was an error, otherwise True.
        """
        # User click on Ok button
        if messageId == c4d.DLG_OK:
            print "User Click on Ok"
            return True

        # User click on Cancel button
        elif messageId == c4d.DLG_CANCEL:
            print "User Click on Cancel"

            # Close the Dialog
            self.Close()
            return True

        return True


def main():
    # Creates a new instance of the GeDialog
    dlg = ExampleDialog()

    # Opens the GeDialog, since it's open it as Modal, it block Cinema 4D
    dlg.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE, defaultw=300, defaulth=50)


if __name__ == "__main__":
    main()
