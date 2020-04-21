"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates and attaches a GeUserArea to a Dialog.
    - Interacts from the GeDialog to the GeUserArea and vice-versa.

Class/method highlighted:
    - c4d.gui.GeDialog
    - c4d.gui.GeUserArea
    - GeDialog.AttachUserArea()
    - GeDialog.Message()
    - GeDialog.SendMessage()
    - GeUserArea.Message()
    - GeUserArea.SendParentMessage()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22
"""
import c4d


GADGET_ID_GEUSERAREA = 10000
GADGET_ID_BUTTON_CHANGE_COLOR = 10001

# Register your own ID at https://plugincafe.maxon.net/c4dpluginid_cp
MSG_ID_CHANGE_COLOR = 1000000

# Register your own ID at https://plugincafe.maxon.net/c4dpluginid_cp
MSG_ID_COLOR_CHANGED = 1000001


class ExampleGeUserArea(c4d.gui.GeUserArea):

    # Color used to draw in the GeUserArea, values are from 0 to 1
    color = c4d.Vector(1, 0, 0)

    def DrawMsg(self, x1, y1, x2, y2, msg):
        # Defines the color used in draw operation
        self.DrawSetPen(self.color)

        # Draws a rectangle filling the whole UI
        self.DrawRectangle(x1, y1, x2, y2)

    def Message(self, msg, result):
        """
        This Method is called automatically when the GeUserArea receives a Message.

        :param msg: The message container.
        :param result: A container to place results in.
        """

        # Messages is sent from the GeDialog at line 107
        if msg.GetId() == MSG_ID_CHANGE_COLOR:
            # Retrieves the color stored in the message
            self.color = msg.GetVector(0)

            # Redraw the GeUserArea (will call DrawMsg)
            self.Redraw()

            # Prepares and sent the message to be send to the host GeDialog.
            # It will inform that the color have been changed
            msgContainer = c4d.BaseContainer(MSG_ID_COLOR_CHANGED)
            self.SendParentMessage(msgContainer)
            return True

        return super(ExampleGeUserArea, self).Message(msg, result)


class ExampleDialog(c4d.gui.GeDialog):
    # The GeUserArea need to be stored somewhere, we will need this instance to be attached to the current Layout
    geUserArea = ExampleGeUserArea()

    def CreateLayout(self):
        """
        This Method is called automatically when Cinema 4D Create the Layout (display) of the Dialog.
        """

        # Adds a Gadget that will host a GeUserArea
        self.AddUserArea(GADGET_ID_GEUSERAREA, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 100, 100)

        # Attaches the stored GeUserArea to the Gadget previously created
        self.AttachUserArea(self.geUserArea, GADGET_ID_GEUSERAREA)

        # Creates a Button, will be used to change the color of the GeUserArea
        self.AddButton(GADGET_ID_BUTTON_CHANGE_COLOR, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, name="Change Color")

        return True

    def Command(self, messageId, bc):
        """
        This Method is called automatically when the user clicks on a gadget and/or changes its value this function will be called.
        It is also called when a string menu item is selected.

        :param messageId: The ID of the gadget that triggered the event.
        :param bc: The original message container
        :return: False if there was an error, otherwise True.
        """
        # User click on the Button to change the color
        if messageId == GADGET_ID_BUTTON_CHANGE_COLOR:

            # Prepares the message to be send to the GeUserArea GeDialog.
            msgContainer = c4d.BaseContainer(MSG_ID_CHANGE_COLOR)
            msgContainer.SetVector(0, c4d.Vector(0, 1, 0))

            # Send the message.
            self.SendMessage(GADGET_ID_GEUSERAREA, msgContainer)

        return True

    def Message(self, msg, result):
        """
        This Method is called automatically when the GeDialog receives a Message.

        :param msg: The message container.
        :param result: A container to place results in.
        """

        # Messages is sent from the GeUserArea in line 65
        if msg.GetId() == MSG_ID_COLOR_CHANGED:
            print("The GeUserArea, has been redraw and color changed.")
            return True

        return super(ExampleDialog, self).Message(msg, result)


def main():
    # Creates a new instance of the GeDialog
    dlg = ExampleDialog()

    # Opens the GeDialog, since it's open it as Modal, it block Cinema 4D
    dlg.Open(c4d.DLG_TYPE_MODAL_RESIZEABLE, defaultw=300, defaulth=50)


if __name__ == "__main__":
    main()