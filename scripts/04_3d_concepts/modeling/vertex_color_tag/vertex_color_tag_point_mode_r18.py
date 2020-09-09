"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Gets and Sets Vertex Colors in Point mode:
    - Changes all black Vertex Colors to red.

Note:
     - Only RGB vertex colors are supported by this script

Class/method highlighted:
    - VertexColorTag.GetDataAddressR()
    - VertexColorTag.GetPoint()
    - VertexColorTag.GetDataAddressW()
    - VertexColorTag.SetPoint()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Retrieves the Vertex Color Tag
    tag = op.GetTag(c4d.Tvertexcolor)
    if tag is None:
        raise TypeError("Failed to retrieve the vertex tag color.")

    # Checks in Point mode
    if not tag.IsPerPointColor():
        # If not changes to Point mode
        tag.SetPerPointMode(True)

    # Obtains vertex colors data R/W addresses
    addrR = tag.GetDataAddressR()
    addrW = tag.GetDataAddressW()

    # Initializes black and red colors
    black = c4d.Vector4d(0, 0, 0, 1)
    red = c4d.Vector4d(1, 0, 0, 1)

    # By default the Vertex Color Tag is in Point mode
    # So GetDataCount() returns the number of points
    count = tag.GetDataCount()
    for idx in range(count):
        # If point color is black then changes it to red
        point = c4d.VertexColorTag.GetPoint(addrR, None, None, idx)
        if point == black:
            c4d.VertexColorTag.SetPoint(addrW, None, None, idx, red)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
