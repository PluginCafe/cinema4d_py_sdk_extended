"""
Copyright: MAXON Computer GmbH
Author: Manuel Magalhaes

Description:
    Retrieve information about the selected port of a selected material.

Class/method highlighted:
    - GetSelectedPorts
    - GetParent
    - GetAncestor
    - GetPortValue
"""
import c4d
import maxon


def main():
    # Create a baseMaterial
    mat = doc.GetActiveMaterial()
    if mat is None:
        raise ValueError("There is no selected BaseMaterial")

    # Retrieve the reference of the material as a node Material.
    nodeMaterial = mat.GetNodeMaterialReference()
    if nodeMaterial is None:
        raise ValueError("can't retrieve nodeMaterial reference")

    # Retrieve the current node space Id
    nodespaceId = c4d.GetActiveNodeSpaceId()

    # Retrieve the graph corresponding to that nodeSpace.
    graph = nodeMaterial.GetGraph(nodespaceId)
    if graph is None:
        raise ValueError("can't retrieve the graph of this nimbus ref")

    def GetName(node):
        """
        Retrieve the displayed name of a node.
        Args:
            node: (maxon.GraphNode): The node to retrieve the name from.

        Returns:
            Optional[str]: The node name, or None if the Node name can't be retrieved.
        """
        if node is None:
            return None

        nodeName = node.GetValue(maxon.NODE.BASE.NAME)

        if nodeName is None:
            nodeName = node.GetValue(maxon.EffectiveName)

        if nodeName is None:
            nodeName = str(node)

        return nodeName

    def RetrieveInformationOfPort(port):
        """
        Retrieve the name of the port, it's value, it's parent name, the name of the true node holding the port
        and if the port is connected the input port name, it is connected.

        This function is used as a callback parameter of GraphHelper.GetSelectedPorts.

        Args:
            port: (maxon.GraphNode): The output port, to query for information.

        Returns:
            bool: **True** if the iteration over ports should continue, otherwise **False**
        """
        if port is None:
            return True

        # Get the port's name
        portName = GetName(port)

        # Get the parent's name of the port, could be another port, a port
        # list or a node.
        directParent = port.GetParent()
        directParentName = GetName(directParent)

        # Try to find the last port to be an ancestor of the selected node.
        # Input or output list are not considered as ancestor.
        ancestorName = None
        # If the directParent is a port list, we will never find the last
        # ancestor port
        kind = (directParent.GetKind() & maxon.NODE_KIND.PORTLIST_MASK)
        if kind != directParent.GetKind():
            # we must start from the parent, otherwise, the port itself will 
            # be returned. (see mask below)
            ancestor = directParent.GetParent()
            # We get the ancestor that is the kind of port.
            ancestor = ancestor.GetAncestor(maxon.NODE_KIND.PORT_MASK)
            ancestorName = GetName(ancestor)

        # We retrieve the node where this port belong to by retrieving the 
        # ancestor with a mask of node kind set to NODE.
        trueNode = port.GetAncestor(maxon.NODE_KIND.NODE)

        trueNodeName = GetName(trueNode)

        # To retrieve and set the value of a port, Set/GetPortValue must 
        # be used.
        portValue = port.GetPortValue()

        # Print the information we gathered.
        msg = (f"The port {portName} have the value {portValue}, the direct "
               f"parent is {directParentName}, the ancestor port is "
               f"{ancestorName} and the port is in the node {trueNodeName}.")
        print(msg)
        return True

    # Print information of the selected ports.
    maxon.GraphModelHelper.GetSelectedNodes(graph, maxon.NODE_KIND.PORT_MASK, RetrieveInformationOfPort)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
