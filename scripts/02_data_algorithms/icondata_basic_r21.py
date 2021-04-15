"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Displays the icon of the selected object into the Picture Viewer.

Class/method highlighted:
    - BaseList2D.GetIconEx()
    - IcoNData.GetClonePart()
    - c4d.bitmaps.ShowBitmap()

Note:
    Before R21 it's possible to call GetIcon which will returns an IconData as a dictionary.

"""
import c4d


def main():
    # Checks if there is an active object
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Retrieves the IconData of the selected object.
    icon = op.GetIconEx()

    # Retrieves a BaseBitmap of the icon
    bmp = icon.GetClonePart()

    # Displays the icon in the Picture Viewer
    c4d.bitmaps.ShowBitmap(bmp)


if __name__ == "__main__":
    main()