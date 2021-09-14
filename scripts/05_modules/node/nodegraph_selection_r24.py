"""
Copyright: MAXON Computer GmbH
Author: Manuel Magalhaes

Description:
    This example shows how to select different elements on a node graph. It 
    creates a node material, select ports, print connections and select wires.
    
Class/method highlighted:
    - BeginTransaction
    - SelectPort
    - SelectWire
"""
import c4d
import maxon
import maxon.frameworks.nodespace
import maxon.frameworks.nodes
import itertools


def main():

    # Create a baseMaterial first
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    if mat is None:
        raise ValueError("Cannot create a BaseMaterial")
    # Insert the material before casting it to a NodeMaterial
    doc.InsertMaterial(mat)

    # Retrieve the reference of the material as a node Material.
    nodeMaterial = mat.GetNodeMaterialReference()
    if nodeMaterial is None:
        raise ValueError("Cannot retrieve nodeMaterial reference")

    # Retrieve the current node space Id
    nodespaceId = c4d.GetActiveNodeSpaceId()

    # Add a graph for the space Id
    addedGraph = nodeMaterial.AddGraph(nodespaceId)
    if addedGraph is None:
        raise ValueError("Cannot add a graphnode for this nodespace")

    # Retrieve the Nimbus reference for a specific nodeSpace
    nimbusRef = mat.GetNimbusRef(nodespaceId)
    if nimbusRef is None:
        raise ValueError("Cannot retrieve the nimbus ref for that node space")

    # Retrieve the graph corresponding to that nodeSpace.
    graph = nimbusRef.GetGraph()
    if graph is None:
        raise ValueError("Cannot retrieve the graph of this nimbus ref")

    # Retrieve the end node of this graph
    endNodePath = nimbusRef.GetPath(
        maxon.frameworks.nodespace.NIMBUS_PATH.MATERIALENDNODE)
    endNode = graph.GetNode(endNodePath)
    if endNode is None:
        raise ValueError("Cannot retrieve the endnode of this graph")

    # Retrieve the predecessors
    predecessor = list()
    endNode.GetDirectPredecessors(predecessor)
    bsdfNode = predecessor[0]
    if bsdfNode is None:
        raise ValueError("Cannot retrieve the node connected to endnode")

    # Retrieve the inputs list of the EndNode
    endNodeInputs = endNode.GetInputs()

    # Retrieve the outputs list of the bsdf node
    bsdfNodeOutputs = bsdfNode.GetOutputs()

    # Select the BSDF node, selected elements are stored inside the graph,
    # so we need a transaction to change it.
    with graph.BeginTransaction() as transaction:
        graph.SelectTrueNode(bsdfNode)
        transaction.Commit()

    # Declare a function that will be used as a callback
    def SelectPort(port):
        graph.SelectPort(port)
        return True

    # Select all the inputs ports of the end node. For that, a transaction
    # need to be created.
    with graph.BeginTransaction() as transaction:
        endNodeInputs.GetChildren(SelectPort)
        transaction.Commit()

    def PrintConnection(port):
        connections = list()
        res = port.GetConnections(
            maxon.frameworks.misc.PORT_DIR.OUTPUT, connections)
        print(port, res, connections)
        for connection in connections:
            graph.SelectWire(port, connection[0])
        return True

    # Select the wire between the material node (end node) and the BSDF node
    # To modify a graph, modification must be done inside a transaction. After
    # modifications are done, the transaction must be committed.
    with graph.BeginTransaction() as transaction:
        bsdfNodeOutputs.GetChildren(PrintConnection)
        transaction.Commit()

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
