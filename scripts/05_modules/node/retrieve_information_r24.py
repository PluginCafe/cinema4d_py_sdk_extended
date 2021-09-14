"""
Copyright: MAXON Computer GmbH
Author: Manuel Magalhaes

Description:
    Retrieve information about the selected port of a selected material.

Class/method highlighted:
    - GetSelectedPorts
    - GetParent
    - GetAncestor
    - GetDefaultValue
"""
import c4d
import maxon
import maxon.frameworks.nodespace
import maxon.frameworks.nodes


def main():

    # Create a baseMaterial first
    mat = doc.GetActiveMaterial()
    if mat is None:
        raise ValueError("can't create a BaseMaterial")

    # Retrieve the reference of the material as a node Material.
    nodeMaterial = mat.GetNodeMaterialReference()
    if nodeMaterial is None:
        raise ValueError("can't retrieve nodeMaterial reference")

    # Retrieve the current node space Id
    nodespaceId = c4d.GetActiveNodeSpaceId()

    # Retrieve the Nimbus reference for a specific nodeSpace
    nimbusRef = mat.GetNimbusRef(nodespaceId)
    if nimbusRef is None:
        raise ValueError("can't retrieve the nimbus ref for that node space")

    # Retrieve the graph corresponding to that nodeSpace.
    graph = nimbusRef.GetGraph()
    if graph is None:
        raise ValueError("can't retrieve the graph of this nimbus ref")

    def GetName(node):
        if node is None:
            return None
        nodeName = None
        nodeName = node.GetValue("net.maxon.node.base.name")
        if nodeName is None:
            nodeName = node.GetValue("effectivename")
        if nodeName is None:
            nodeName = str(node)
        return nodeName

    def RetrieveInformationOfPort(port):

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
        kind = (directParent.GetKind() &
                maxon.frameworks.graph.NODE_KIND.PORTLIST_MASK)
        if kind != directParent.GetKind():
            # we must start from the parent, otherwise, the port itself will 
            # be returned. (see mask below)
            ancestor = directParent.GetParent()
            # We get the ancestor that is the kind of port.
            ancestor = ancestor.GetAncestor(
                maxon.frameworks.graph.NODE_KIND.PORT_MASK)
            ancestorName = GetName(ancestor)

        # We retrieve the node where this port belong to by retrieving the 
        # ancestor with a mask of node kind set to NODE.
        trueNode = port.GetAncestor(maxon.frameworks.graph.NODE_KIND.NODE)
        trueNodeName = GetName(trueNode)

        # To retrieve and set the value of a port, Set/GetDefaultValue must 
        # be used.
        portValue = port.GetDefaultValue()

        # Print the information we gathered.
        msg = (f"The port {portName} have the value {portValue}, the direct "
               f"parent is {directParentName}, the ancestor port is "
               f"{ancestorName} and the port is in the node {trueNodeName}.")
        print(msg)
        return True

    # Print information of the selected ports.
    graph.GetSelectedPorts(RetrieveInformationOfPort)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
