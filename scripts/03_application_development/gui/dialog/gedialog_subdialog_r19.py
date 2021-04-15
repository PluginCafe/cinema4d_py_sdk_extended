"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates and attaches a SubDialog to a Dialog.
    - Switch the displayed SubDialog after a click on a button.

Class/method highlighted:
    - c4d.gui.GeDialog
    - c4d.gui.GeDialog.SubDialog
    - GeDialog.AttachSubDialog()

"""
import c4d


GADGET_ID_SUBDIALOG = 10000
GADGET_ID_BUTTON_SWITCH_SUBDIALOG = 10001


class AnotherSubDialogExample(c4d.gui.SubDialog):

    def CreateLayout(self):
        """This Method is called automatically when Cinema 4D Create the Layout (display) of the SubDialog."""

        # Creates a Static Text
        self.AddStaticText(1000, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, 0, "Second Sub Dialog", c4d.BORDER_THIN_IN)

        return True


class SubDialogExample(c4d.gui.SubDialog):

    def CreateLayout(self):
        """This Method is called automatically when Cinema 4D Create the Layout (display) of the SubDialog."""

        # Creates a Static Text
        self.AddStaticText(1000, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, 0, "First Sub Dialog", c4d.BORDER_THIN_IN)

        return True


class ExampleDialog(c4d.gui.GeDialog):

    # The SubDialog need to be stored somewhere, we will need this instance to be attached to the current Layout
    subDialog = SubDialogExample()

    def CreateLayout(self):
        """This Method is called automatically when Cinema 4D Create the Layout (display) of the Dialog."""

        # Adds a Gadget that will host a SubDialog
        self.AddSubDialog(GADGET_ID_SUBDIALOG, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 100, 100)

        # Attaches the stored SubDialog to the Gadget previously created
        self.AttachSubDialog(self.subDialog, GADGET_ID_SUBDIALOG)

        # Creates a Button, will be used to change the SubDialog displayed
        self.AddButton(GADGET_ID_BUTTON_SWITCH_SUBDIALOG, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, name="Switch SubDialog")

        return True

    def Command(self, messageId, bc):
        """This Method is called automatically when the user clicks on a gadget and/or changes its value this function will be called.
        It is also called when a string menu item is selected.

        Args:
            messageId: The ID of the gadget that triggered the event.
            bc: The original message container

        Returns:
            False if there was an error, otherwise True.
        """
        # User click on the Switch Button
        if messageId == GADGET_ID_BUTTON_SWITCH_SUBDIALOG:
            # Stores the instance of the new SubDialog
            self.subDialog = AnotherSubDialogExample()

            # Attaches the stored SubDialog to the Gadget previously created
            self.AttachSubDialog(self.subDialog, GADGET_ID_SUBDIALOG)

            # Informs the Dialog, that this Gadget have changed and need to be redraw
            self.LayoutChanged(GADGET_ID_SUBDIALOG)

        return True


def main():
    # Creates a new instance of the GeDialog
    dlg = ExampleDialog()

    # Opens the GeDialog, since it's open it as Modal, it block Cinema 4D
    dlg.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE, defaultw=300, defaulth=50)


if __name__ == "__main__":
    main()