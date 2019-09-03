"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Deletes the first node created from the Xpresso Tag of the selected object.

Class/method highlighted:
    - c4d.modules.graphview.GvNodeMaster
    - c4d.modules.graphview.GvNode
    - GvNodeMaster.GetRoot()
    - GeListNode.GetDown()
    - GeListNode.Remove()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21
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

    # Retrieves the Root node (the Main XGroup) that holds all others nodes
    gvRoot = gvNodeMaster.GetRoot()
    if gvRoot is None:
        raise RuntimeError("Failed to retrieve the Root Node.")

    # Gets the first child
    firstNode = gvRoot.GetDown()
    if firstNode is None:
        raise RuntimeError("Failed to retrieve the First Node.")

    # GvNode is a GeListNode so you can simply use Remove
    firstNode.Remove()

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()