"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam
Description:
    - Creates a Modal Dialog displaying a different SubDialog according to the selected entry of the QuickTab.
    - Demonstrates how to add, flushes, remove tab interactively.
Class/method highlighted:
    - c4d.gui.QuickTabCustomGui
    - QuickTabCustomGui.ClearStrings()
    - QuickTabCustomGui.AppendString()
    - c4d.gui.GeDialog
    - GeDialog.CreateLayout()
    - GeDialog.InitValues()
    - GeDialog.Command()
    - GeDialog.HideElement()
    - GeDialog.RemoveElement()
    - c4d.gui.SubDialog
Compatible:
    - Win / Mac
    - R19, R20, R21
"""
import c4d

# Ids used in our Dialog
ID_MAINGROUP = 100000  # ID used for the Group that holds all the other group representing the tab content
ID_QUICKTAB_BAR = 110000  # ID for the quicktab customGui
ID_QUICKTAB_BASE_GROUP = 120000  # Base ID for each SubDialog

BUTTON_PRINT_TEXT = 1200  # ID used for the Print text Button
BUTTON_PRINT_SELECTED = 1201  # ID used for the Print Selected Button
BUTTON_FLUSH_ALL = 1203  # ID used for the Flush All Button
BUTTON_ADD = 1204  # ID used for the Add Button
BUTTON_REMOVE = 1205  # ID used for the Remove Button

# Id used in our SubDialog
CUSTOM_GROUP_ID_TEXT_BASE = 100000  # Defines the ID for the string to be displayed


class CustomGroup(c4d.gui.SubDialog):
    """
    A SubDialog to display the passed string, its used as example for the actual content of a Tab
    """
    def __init__(self, data):
        self._data = data

    def CreateLayout(self):
        for i, data in enumerate(self._data):
            self.AddStaticText(CUSTOM_GROUP_ID_TEXT_BASE + i, c4d.BFH_SCALEFIT, name=data)
        return True


class QuickTabDialogExample(c4d.gui.GeDialog):

    def __init__(self):
        self._quickTab = None  # Stores the quicktab custom GUI
        self._tabList = {}  # Stores the TabName and the SubDialog that represents each tab of the QuickTab

    def _DrawQuickTabGroup(self):
        """
        Creates and draws all the SubDialog for each tab, take care it does not hide these according to a selection state.
        :return: True if success otherwise False.
        """

        # Checks if the quicktab is defined
        if self._quickTab is None:
            return False

        # Flush the content of the group that holds all ours SubDialogs
        self.LayoutFlushGroup(ID_MAINGROUP)

        # Iterates over the number of tab to create and attach the correct SubDialog
        for tabId, (tabName, tabGui) in enumerate(self._tabList.iteritems()):
            self.AddSubDialog(ID_QUICKTAB_BASE_GROUP + tabId, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, 0)
            self.AttachSubDialog(tabGui, ID_QUICKTAB_BASE_GROUP + tabId)

        # Notifies the content of the MainGroup has changed
        self.LayoutChanged(ID_MAINGROUP)

        return True

    def GetActiveTabs(self):
        """
        Retrieves two list of currently selected tabs from the self._quickTab.
        :return: The first list, contains tabs Id (from self._quickTab the dict) and the second list contains all names of the selected tabs.
        :rtype: list(int), list(name)
        """
        # Checks if the quicktab is defined
        if self._quickTab is None:
            return False, False

        returnIds = []
        returnNames = []

        for tabId, (tabName, tabGui) in enumerate(self._tabList.iteritems()):
            if self._quickTab.IsSelected(tabId):
                returnIds.append(tabId)
                returnNames.append(tabName)

        return returnIds, returnNames

    def DisplayCorrectGroup(self):
        """
        Hides all unused groups and display the correct one.
        :return: True if success otherwise False.
        """
        # Retrieves the selected tab
        activeIds, activeNames = self.GetActiveTabs()

        # Iterates each CustomGui and defines if they are hidden or not
        for tabId in xrange(len(self._tabList)):
            toDisplay = tabId in activeIds
            self.HideElement(ID_QUICKTAB_BASE_GROUP + tabId, not toDisplay)

        # Notifies the content of the MainGroup has changed
        self.LayoutChanged(ID_MAINGROUP)
        return True

    def AppendTab(self, tabName, content, active=True):
        """
        Appends a tab to the current quicktab with the associated content to be displayed.
        :param tabName: The name the tab should have.
        :type tabName: str
        :param content: The SubDialog to be drawn/linked when the tab is selected.
        :type content: c4d.gui.SubDialog
        :param active: If True, the inserted tab will be selected
        :type active: bool
        :return: True if success otherwise False.
        """
        # Checks if the quicktab is defined
        if self._quickTab is None:
            return False

        # Adds the tab entry n the quicktab
        self._quickTab.AppendString(len(self._tabList), tabName, False)

        # Updates our current tabList with tabName and the Subdialog to be linked
        self._tabList.update({tabName: content})

        # Retrieves the current selected tab
        previousActiveId, previousActiveName = self.GetActiveTabs()

        # Draws the quicktab SubDialog (in order to have the new one drawn)
        self._DrawQuickTabGroup()

        # Defines the just added tab according state
        self._quickTab.Select(len(self._tabList) - 1, active)

        # Defines previous active tab
        for tabId in previousActiveId:
            self._quickTab.Select(tabId, True)

        # Display only the selected tab and hides all others
        self.DisplayCorrectGroup()

        return True

    def FlushAllTabs(self):
        """
        Removes all tabs and their content from the GUI.
        :return: True if success otherwise False.
        """
        # Checks if the quicktab is defined
        if self._quickTab is None:
            return False

        # Removes all the tabs
        self._quickTab.ClearStrings()

        # Removes all the customGui
        for tabId in xrange(len(self._tabList)):
            self.RemoveElement(ID_QUICKTAB_BASE_GROUP + tabId)

        # Reinitializes the stored tablist to an empty dict
        self._tabList = {}

        # Notifies the content of the MainGroup has changed
        self.LayoutChanged(ID_MAINGROUP)

        return True

    def RemoveTab(self, tabNameToRemove):
        """
        Removes a tab by its name
        :param tabNameToRemove: The tab to remove.
        :type tabNameToRemove: str
        :return: True if success otherwise False.
        """
        # Checks if the quicktab is defined
        if self._quickTab is None:
            return False

        # Copies the tabList
        newDict = dict(self._tabList)

        # Checks if the entry exist
        if tabNameToRemove not in newDict:
            return True

        # Removes the entry we want to delete
        del newDict[tabNameToRemove]

        # Removes all groups
        self.FlushAllTabs()

        # Re-adds all the one from our copy
        for tabName, tabGui in newDict.iteritems():
            self.AppendTab(tabName, tabGui)

        return True

    def CreateLayout(self):
        """
        This Method is called automatically when Cinema 4D Create the Layout (display) of the Dialog.
        """

        # Creates a QuickTab Custom Gui
        bc = c4d.BaseContainer()
        bc.SetBool(c4d.QUICKTAB_BAR, False)
        bc.SetBool(c4d.QUICKTAB_SHOWSINGLE, True)
        bc.SetBool(c4d.QUICKTAB_NOMULTISELECT, False)
        self._quickTab = self.AddCustomGui(ID_QUICKTAB_BAR, c4d.CUSTOMGUI_QUICKTAB, '',
                                           c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, 0, bc)

        # Creates a group that will contain all the group representing each tab
        self.GroupBegin(ID_MAINGROUP, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 0, 0, '', 0)
        self.GroupEnd()

        # Creates a group with 5 button in order to do some operation with the QuickTab CustomGUI
        if self.GroupBegin(0, c4d.BFH_SCALEFIT, 5, 1, '', 0):
            self.AddButton(BUTTON_PRINT_TEXT, c4d.BFH_SCALEFIT, name="Print text")
            self.AddButton(BUTTON_PRINT_SELECTED, c4d.BFH_SCALEFIT, name="Print Selected")
            self.AddButton(BUTTON_FLUSH_ALL, c4d.BFH_SCALEFIT, name="Flush All")
            self.AddButton(BUTTON_ADD, c4d.BFH_SCALEFIT, name="Add")
            self.AddButton(BUTTON_REMOVE, c4d.BFH_SCALEFIT, name="Remove")
        self.GroupEnd()
        return True

    def InitValues(self):
        """
        This Method is called automatically after the GUI is initialized.
        """
        # Creates the first Tab
        cg1 = CustomGroup(["This is the first Tab", "Just dummy text here"])
        self.AppendTab("First Tab", cg1, True)

        # Creates the second Tab
        cg2 = CustomGroup(["This is the second Tab", "Just another dummy text here"])
        self.AppendTab("Second Tab", cg2, False)
        return True

    def Command(self, id, msg):
        """
         This Method is called automatically when the user clicks on a gadget and/or changes its value this function will be called.
         It is also called when a string menu item is selected.
        :param id: The ID of the gadget that triggered the event.
        :param msg: The original message container
        :return: False if there was an error, otherwise True.
        """

        # If the user interacts with the quicktab, we make sure to display the CustomGUI linked to the active one
        if id == ID_QUICKTAB_BAR and self._quickTab:
            self.DisplayCorrectGroup()
            return True

        # Displays all the Tab name
        if id == BUTTON_PRINT_TEXT:
            print [key for key in self._tabList]
            return True

        # Displays the ID and name of the selected tab
        if id == BUTTON_PRINT_SELECTED:
            print self.GetActiveTabs()

        # Removes all tabs
        if id == BUTTON_FLUSH_ALL:
            self.FlushAllTabs()

        # Adds a new Tab to the quicktab
        if id == BUTTON_ADD:
            cg3 = CustomGroup(["This is the third Tab"])
            self.AppendTab("Third Tab", cg3, True)

        # Removes the first tab of the quicktab
        if id == BUTTON_REMOVE:
            self.RemoveTab("First Tab")

        return True


# Main function
def main():
    # Initializes a QuickTabDialogExample Dialog
    diag = QuickTabDialogExample()

    # Opens the Dialog in modal mode
    diag.Open(dlgtype=c4d.DLG_TYPE_MODAL, defaultw=400, defaulth=400)


# Execute main()
if __name__ == '__main__':
    main()
