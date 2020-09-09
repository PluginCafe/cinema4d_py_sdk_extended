"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Retrieves the Node Master (The BaseList2D object that holds all nodes) from an Xpresso Tag.

Class/method highlighted:
    - c4d.modules.graphview.GvNodeMaster

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Retrieves the xpresso Tag
    xpressoTag = op.GetTag(c4d.Texpresso)
    if xpressoTag is None:
        raise ValueError("Make sure the selected object get an Xpresso Tag.")

    # Retrieves the node master
    gvNodeMaster = xpressoTag.GetNodeMaster()
    if gvNodeMaster is None:
        raise RuntimeError("Failed to retrieve the Node Master.")

    print(gvNodeMaster)


if __name__ == '__main__':
    main()
