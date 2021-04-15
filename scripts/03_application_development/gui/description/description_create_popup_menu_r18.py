"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Retrieves a BaseContainer with all the parameters of an object.

Class/method highlighted:
    - Description.CreatePopupMenu()

"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Retrieves the active object's description
    desc = op.GetDescription(c4d.DESCFLAGS_DESC_0)
    if desc is None:
        raise RuntimeError("Failed to retrieve the description.")

    # Retrieves the container with all the object's parameters
    menu = desc.CreatePopupMenu()

    # Shows the menu as a popup dialog
    c4d.gui.ShowPopupDialog(cd=None, bc=menu, x=c4d.MOUSEPOS, y=c4d.MOUSEPOS)


if __name__ == '__main__':
    main()
