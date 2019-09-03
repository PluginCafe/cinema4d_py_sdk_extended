"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates an async Dialog with a top menu.
    - Defines an icon in the menu to toggle group visibility.

Class/method highlighted:
    - c4d.gui.GeDialog
    - GeDialog.CreateLayout()
    - c4d.gui.BitmapButtonCustomGui
    - GeDialog.MenuFlushAll()
    - GeDialog.MenuAddString()
    - GeDialog.InitValues()
    - GeDialog.HideElement()
    - GeDialog.Command()
    - GeDialog.LayoutChanged()

Compatible:
    - Win / Mac
    - R15, R16, R17, R18, R19, R20, R21
"""
import c4d


class MenuDlg(c4d.gui.GeDialog):
    ID_LEFT_MENU_FIRST_ITEM = 10000
    ID_RIGHT_MENU_SHOW_CONTENT = 10001
    ID_MAIN_GROUP = 10002
    ID_HIDDEN_GROUP = 10003

    displayContentButtonDlg = None
    toogleState = True

    def CreateLayout(self):
        """
        This method is called automatically when Cinema 4D Create the Layout (display) of the Dialog.
        """
        # Defines the title of the Dialog
        self.SetTitle("A Custom Dialog with a Top Menu")

        # Flushes all the already existing menu to create our one. The content will be on the left.
        self.MenuFlushAll()

        # Creates a Sub menu begin to insert new menu entry
        self.MenuSubBegin("Left Menu")

        # Adds a string with a given ID, so it will trigger a call to Command once clicked
        self.MenuAddString(self.ID_LEFT_MENU_FIRST_ITEM, "Close")

        # Finalizes the Sub Menu
        self.MenuSubEnd()

        # Finalizes the menu
        self.MenuFinished()

        # Creates a Group in the Menu. The content will be on the right
        if self.GroupBeginInMenuLine():
            # Creates a BitmapButtonCustomGui with the find icon
            settings = c4d.BaseContainer()
            settings[c4d.BITMAPBUTTON_BUTTON] = True
            settings[c4d.BITMAPBUTTON_BORDER] = False
            settings[c4d.BITMAPBUTTON_TOGGLE] = True
            settings[c4d.BITMAPBUTTON_ICONID1] = c4d.RESOURCEIMAGE_SCENEBROWSER_FIND2
            settings[c4d.BITMAPBUTTON_ICONID2] = c4d.RESOURCEIMAGE_SCENEBROWSER_FIND1

            self.displayContentButtonDlg = self.AddCustomGui(self.ID_RIGHT_MENU_SHOW_CONTENT,
                                                             c4d.CUSTOMGUI_BITMAPBUTTON, "",
                                                             c4d.BFH_CENTER | c4d.BFV_CENTER, 0, 0, settings)

        self.GroupEnd()

        # Creates a group that will contain the content that will be hidden when the BitmapButton is pressed. It's
        # important to have a parent group to the group that needs to be hidden since you need to redraw this parent
        # group after the visibility definition.
        if self.GroupBegin(self.ID_MAIN_GROUP, c4d.BFH_LEFT | c4d.BFV_CENTER):

            # The group that will be hidden
            if self.GroupBegin(self.ID_HIDDEN_GROUP, c4d.BFH_LEFT | c4d.BFV_CENTER):
                # Adds the content you want to toggle
                self.AddStaticText(0, c4d.BFH_LEFT | c4d.BFV_CENTER, name="test")

            self.GroupEnd()
        self.GroupEnd()

        # Adds two buttons, Ok and Cancel
        self.AddDlgGroup(c4d.DLG_OK | c4d.DLG_CANCEL)

        return True

    def InitValues(self):
        """
        This method is called automatically after the GUI is initialized.
        """
        # Defines the initial hidden state of the group according the the value stored.
        self.HideElement(self.ID_HIDDEN_GROUP, self.toogleState)
        return True

    def Command(self, id, msg):
        """
        This method is called automatically when the user clicks on a gadget and/or changes its value
        this function will be called.
        It is also called when a string menu item is selected.

        :param id: The ID of the gadget that triggered the event.
        :param msg: The original message container
        :return: False if there was an error, otherwise True.
        """

        # If the user click on the "Close" item of the menu
        if id == self.ID_LEFT_MENU_FIRST_ITEM:
            self.Close()

        # If the user click on the bitmap button from the menu
        elif id == self.ID_RIGHT_MENU_SHOW_CONTENT:
            # Updates the stored value of the toggle state
            self.toogleState = not self.toogleState

            # Hides the element
            self.HideElement(self.ID_HIDDEN_GROUP, self.toogleState)

            # Notifies that the content of the parent group of the group we just hide has changed and need to be redrawn
            self.LayoutChanged(self.ID_MAIN_GROUP)

        return True


def main():
    # Quick hack since menu can only be displayed in an async dialog
    # Please don't do this on production, instead create a CommandData to store the GeDialog instance
    global diag

    # Creates an instance of the object MenuDlg
    diag = MenuDlg()

    # Opens the Dialog, Cinema 4D will then call CreateLayout, InitValues and so on...
    diag.Open(dlgtype=c4d.DLG_TYPE_ASYNC, defaultw=-2, defaulth=-2)


if __name__ == '__main__':
    main()