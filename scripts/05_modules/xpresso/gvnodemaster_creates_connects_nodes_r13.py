"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a Constants and Results node in the Xpresso Tag of the selected object.
    - Connects both Nodes together.

Class/method highlighted:
    - c4d.modules.graphview.GvNodeMaster
    - c4d.modules.graphview.GvNode
    - c4d.modules.graphview.GvPort
    - GvNodeMaster.GetRoot()
    - GvNodeMaster.CreateNode()
    - GvPort.Connect()


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

    # Creates a constant node in the GvRoot
    constNode = gvNodeMaster.CreateNode(gvRoot, c4d.ID_OPERATOR_CONST, x=100, y=100)
    if constNode is None:
        raise RuntimeError("Failed to create the const Node.")

    # Assigns value
    constNode[c4d.GV_CONST_VALUE] = 10.5

    # Creates a result node in the GvRoot (Main XGroup)
    resNode = gvNodeMaster.CreateNode(gvRoot, c4d.ID_OPERATOR_RESULT, x=200, y=100)
    if resNode is None:
        raise RuntimeError("Failed to create the result Node.")

    # Retrieves the first output port of the Const Node
    outPortConstNode = constNode.GetOutPort(0)
    if outPortConstNode is None:
        raise RuntimeError("Failed to retrieve the output port of the constant node.")

    # Retrieves the first input port of the Result Node
    inPortResNode = resNode.GetInPort(0)
    if inPortResNode is None:
        raise RuntimeError("Failed to retrieve the input port of the result node.")

    # Checks the two port are not already connected should never happen since we just created the node
    if inPortResNode in outPortConstNode.GetDestination():
        raise RuntimeError("Input port and Output port are already connected.")

    # Connects the output port of the Const Node to the input port of the Result Node.
    # Always do this in this way, Output connects to Input.
    if not outPortConstNode.Connect(inPortResNode):
        raise RuntimeError("Failed to connect the output to the input port.")

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()