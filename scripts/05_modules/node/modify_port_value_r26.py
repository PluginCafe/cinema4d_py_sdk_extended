"""
Copyright: MAXON Computer GmbH
Author: Manuel Magalhaes

Description:
    Create a material for the standard node space and modify the value of the 
    BDSF color port.
    
Class/method highlighted:
    - SetPortValue
    - GetDirectPredecessors
    - FindChild
"""
import c4d
import maxon


def main():
    # Retrieve the selected baseMaterial
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    if mat is None:
        raise ValueError("Cannot create a BaseMaterial")

    # Retrieve the reference of the material as a node Material.
    nodeMaterial = mat.GetNodeMaterialReference()
    if nodeMaterial is None:
        raise ValueError("Cannot retrieve nodeMaterial reference")

    # Define the ID of standard material node space and print a warning when the active node space
    # is not the the standard material node space.
    nodeSpaceId = maxon.Id("net.maxon.nodespace.standard")
    if nodeSpaceId != c4d.GetActiveNodeSpaceId():
        print (f"Warning: Active node space is not: {nodeSpaceId}")

    # Add a graph for the standard node space.
    addedGraph = nodeMaterial.CreateDefaultGraph(nodeSpaceId)
    if addedGraph is None:
        raise ValueError("Cannot add a graph node for this node space")

    # Retrieve the Nimbus reference for a specific node space from which we 
    # will retrieve the graph. One could also use 'addedGraph' defined above.
    nimbusRef = mat.GetNimbusRef(nodeSpaceId)
    if nimbusRef is None:
        raise ValueError("Cannot retrieve the nimbus ref for that node space")

    # Retrieve the graph corresponding to that node space.
    graph = nimbusRef.GetGraph()
    if graph is None:
        raise ValueError("Cannot retrieve the graph of this nimbus ref")

    # Retrieve the end node of this graph
    endNodePath = nimbusRef.GetPath(maxon.NIMBUS_PATH.MATERIALENDNODE)
    endNode = graph.GetNode(endNodePath)
    if endNode is None:
        raise ValueError("Cannot retrieve the end-node of this graph")

    # Retrieve the predecessors. Function have been moved in R26.
    predecessor = list()
    maxon.GraphModelHelper.GetDirectPredecessors(endNode, maxon.NODE_KIND.NODE,  predecessor)
    bsdfNode = predecessor[0]
    if bsdfNode is None:
        raise ValueError("Cannot retrieve the node connected to end-node")

    # Retrieve the outputs list of the BDSF node
    if bsdfNode is None and not bsdfNode.IsValid() :
        raise ValueError(
            "Cannot retrieve the inputs list of the bsdfNode node")
    bsdfNodeInputs = bsdfNode.GetInputs()
    colordePort = bsdfNodeInputs.FindChild("color")
    if colordePort is None:
        return

    with graph.BeginTransaction() as transaction:
        # Define the value of the Color's port.
        colordePort.SetPortValue(maxon.ColorA(1, 0, 0, 1))
        transaction.Commit()

    # Insert the material to the document.
    doc.InsertMaterial(mat)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
