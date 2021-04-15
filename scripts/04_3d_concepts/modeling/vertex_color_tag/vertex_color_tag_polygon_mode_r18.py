"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Gets and Sets Vertex Colors in Polygon mode:
    - Changes all vertex colors to red.

Note:
     - Only RGB vertex colors are supported by this script

Class/method highlighted:
    - VertexColorTag.GetDataAddressW()
    - VertexColorTag.SetPolygon()

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
    if tag.IsPerPointColor():
        # If not changes to Polygon mode
        tag.SetPerPointMode(False)

    # Obtains Vertex Colors data address
    addr = tag.GetDataAddressW()

    # Initializes red color and Vertex Colors polygon
    red = c4d.Vector4d(1, 0, 0, 1)
    poly = dict()
    poly['a'] = red
    poly['b'] = red
    poly['c'] = red
    poly['d'] = red

    # GetDataCount() returns the number of polygons in Polygon mode
    count = tag.GetDataCount()
    for idx in range(count):
        # Sets Vertex Colors red
        c4d.VertexColorTag.SetPolygon(addr, idx, poly)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
