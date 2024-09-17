"""
Copyright: MAXON Computer GmbH
Author: Manuel Magalhaes

Description:
    Retrieve the selected node material and group the node that are selected.
    
Class/method highlighted:
    - MoveToGroup
    - IsNodeSelected
"""
import c4d
import maxon


def main():
    # Retrieve the selected BaseMaterial
    mat = doc.GetActiveMaterial()
    if mat is None:
        raise ValueError("There is no selected BaseMaterial")

    # Retrieve the reference of the material as a node material.
    nodeMaterial = mat.GetNodeMaterialReference()
    if nodeMaterial is None:
        raise ValueError("Cannot retrieve node material reference")

    # Retrieve the current node space Id
    nodespaceId = c4d.GetActiveNodeSpaceId()

    # Retrieve the Nimbus reference for a specific node space
    nimbusRef = mat.GetNimbusRef(nodespaceId)
    if nimbusRef is None:
        raise ValueError("Cannot retrieve the nimbus ref for that node space")

    # Retrieve the graph corresponding to that node space.
    graph = nimbusRef.GetGraph()
    if graph is None:
        raise ValueError("Cannot retrieve the graph of this nimbus ref")

    # Get the root of the GraphNode
    root = graph.GetViewRoot()

    # Retrieve all nodes, child of the root node
    nodes = []
    root.GetChildren(nodes, maxon.NODE_KIND.NODE)

    # Create a list of the selected ones.
    selectedNodes = []

    for node in nodes:
        if maxon.GraphModelHelper.IsNodeSelected(node):
            selectedNodes.append(node)

    # Group all the selected nodes in an empty node.
    groupRoot = maxon.GraphNode()

    # To modify a graph, modification must be done inside a transaction. After
    # modifications are done, the transaction must be committed.
    with graph.BeginTransaction() as transaction:
        graph.MoveToGroup(groupRoot, maxon.Id("idOfMyGroup"), selectedNodes)
        transaction.Commit()

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
