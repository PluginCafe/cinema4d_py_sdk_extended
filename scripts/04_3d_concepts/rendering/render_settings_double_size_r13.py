"""
Copyright: MAXON Computer GmbH
Author: XXX

Description:
    - Double the size of the render from the active Render Settings.

Class/method highlighted:
    - BaseDocument.GetActiveRenderData()

"""
import c4d


def main():
    # Gets the current active render settings
    rdata = doc.GetActiveRenderData()

    # Doubles the output size
    rdata[c4d.RDATA_XRES] *= 2
    rdata[c4d.RDATA_YRES] *= 2

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
