"""
Copyright: MAXON Computer GmbH
Author: Manuel Magalhaes

Description:
    Create a material for the standard node space and modify the value of the 
    BDSF color port.
    
Class/method highlighted:
    - SetDefaultValue
    - GetDirectPredecessors
    - FindChild
"""
import c4d
import maxon
import maxon.frameworks.nodespace
import maxon.frameworks.nodes


def main():
    # Retrieve the selected baseMaterial
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    if mat is None:
        raise ValueError("Cannot create a BaseMaterial")

    # Retrieve the reference of the material as a node Material.
    nodeMaterial = mat.GetNodeMaterialReference()
    if nodeMaterial is None:
        raise ValueError("Cannot retrieve nodeMaterial reference")

    # Create the node space ID for the standard's node space
    nodespaceId = maxon.Id("net.maxon.nodespace.standard")

    # Add a graph for the standard node space
    addedGraph = nodeMaterial.AddGraph(nodespaceId)
    if addedGraph is None:
        raise ValueError("Cannot add a graph node for this node space")

    # Retrieve the Nimbus reference for a specific node space from which we 
    # will retrieve the graph. One could also use 'addedGraph' defined above.
    nimbusRef = mat.GetNimbusRef(nodespaceId)
    if nimbusRef is None:
        raise ValueError("Cannot retrieve the nimbus ref for that node space")

    # Retrieve the graph corresponding to that node space.
    graph = nimbusRef.GetGraph()
    if graph is None:
        raise ValueError("Cannot retrieve the graph of this nimbus ref")

    # Retrieve the end node of this graph
    endNodePath = nimbusRef.GetPath(
        maxon.frameworks.nodespace.NIMBUS_PATH.MATERIALENDNODE)
    endNode = graph.GetNode(endNodePath)
    if endNode is None:
        raise ValueError("Cannot retrieve the end-node of this graph")

    # Retrieve the predecessors
    predecessor = list()
    endNode.GetDirectPredecessors(predecessor)
    bsdfNode = predecessor[0]
    if bsdfNode is None:
        raise ValueError("Cannot retrieve the node connected to end-node")

    # Retrieve the outputs list of the BDSF node
    bsdfNodeInputs = bsdfNode.GetInputs()
    if bsdfNode is None:
        raise ValueError(
            "Cannot retrieve the inputs list of the bsdfNode node")

    colordePort = bsdfNodeInputs.FindChild("color")
    if colordePort is None:
        return

    with graph.BeginTransaction() as transaction:
        # Define the value of the Color's port.
        colordePort.SetDefaultValue(maxon.ColorA(1, 0, 0, 1))
        transaction.Commit()

    # Insert the material to the document.
    doc.InsertMaterial(mat)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
