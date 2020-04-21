# Dialog

The Cinema 4D GUI is based on "dialog" windows based on the GeDialog class. A plugin can create custom dialog windows for user interaction or to create new managers.

GeDialog is the base class for custom dialogs, see GeDialog Manual.
The layout and gadgets of GeDialog window can be defined using text-based resource files. See Resource Files Manual.
GeUserArea is the base class for custom gadgets used with dialogs, see GeUserArea Manual.

Classic API:
- **c4d.gui**: *Class storing statics methods for general Cinema 4D GUI handling.*
- **c4d.gui.GeDialog**: *GeDialog is the base class for interface elements of Cinema 4D. A custom dialog is added by creating a subclass of GeDialog.*
- **c4d.gui.SubDialog**: *This class is for creating sub-dialogs that can be attached to a SubDialog Gadget in an ordinary GeDialog with GeDialog.AttachSubDialog().*
- **c4d.gui.GeUserArea**: *GeUserArea is the base class for all gadgets that can be displayed in a GeDialog. A new gadget is created by implementing a subclass of GeUserArea.*

## Examples

### customgui_quicktab
Version: R19, R20, R21, S22 - Win/Mac

    Creates a Modal Dialog displaying a different SubDialog according to the selected entry of the QuickTab.
    Demonstrates how to add, flushes, remove tab interactively.

### gedialog_ask_number
Version: R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Creates a Modal Dialog asking for an integer or a float.
    Retrieves the entered value, once the user exit the Dialog.

### gedialog_menu_hide_content
Version: R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Creates an async Dialog with a top menu.
    Defines an icon in the menu to toggle group visibility.

### gedialog_modal
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Creates a basic Modal Dialog.
    
### gedialog_subdialog
Version: R19, R20, R21, S22 - Win/Mac

    Creates and attaches a SubDialog to a Dialog.
    Switch the displayed SubDialog after a click on a button.

### geuserarea_basic
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Creates and attaches a GeUserArea to a Dialog.
    Interacts from the GeDialog to the GeUserArea and vice-versa.

### geuserarea_drag
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Creates and attaches a GeUserArea to a Dialog.
    Creates a series of aligned squares, that can be dragged and swapped together.
