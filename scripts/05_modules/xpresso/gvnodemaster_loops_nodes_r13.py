"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Loops through all nodes from the Xpresso Tag of the selected object.
    - Checks if it's a Constant Node.

Class/method highlighted:
    - c4d.modules.graphview.GvNodeMaster
    - c4d.modules.graphview.GvNode
    - GvNodeMaster.GetRoot()
    - GvNode.GetNext() / GvNode.GetUp() / GvNode.GetDown()
    - GvNode.GetOperatorID()


Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23
"""
import c4d


def iterateNodes(node):
    """
    This function iterates over a BaseList2D, GvNode inherit from BaseList2D.
    :param node: GvNode to iterate.
    """
    while node:
        nodeName = node.GetName()
        isConstantNode = node.GetOperatorID() == c4d.ID_OPERATOR_CONST

        # If there is no parent, this means it's the gvNodeMaster.GetRoot() node, typically the master node
        parent = node.GetUp().GetName() if node.GetUp() is not None else "Master XGroup"

        print("Name: {0}, Is Constant Node: {1}, Parent: {2}".format(nodeName, isConstantNode, parent))

        # If it's a group retrieves all inner GvNode.
        if node.IsGroupNode():
            iterateNodes(node.GetDown())

        node = node.GetNext()


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

    # Iterates overs all nodes of this root node.
    iterateNodes(gvRoot)


if __name__ == '__main__':
    main()
