"""
Copyright: MAXON Computer GmbH
Author: Manuel Magalhaes

Description:
    This example shows how to solo a node. It creates a material and solo's 
    the end node in this material.
    
Class/method highlighted:
    - GetPath
    - GetSoloNodePath
    - SetPath
"""
import c4d
import maxon


def main():
    # Create a baseMaterial
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    if mat is None:
        raise ValueError("Cannot create a BaseMaterial")

    # Retrieve the reference of the material as a node Material
    nodeMaterial = mat.GetNodeMaterialReference()
    if nodeMaterial is None:
        raise ValueError("Cannot retrieve nodeMaterial reference")

    # Retrieve the current node space Id
    nodespaceId = c4d.GetActiveNodeSpaceId()

    # Add a graph for the space Id
    addedGraph = nodeMaterial.CreateDefaultGraph(nodespaceId)
    if addedGraph is None:
        raise ValueError("Cannot add a graphnode for this nodespace")

    # Retrieve the Nimbus reference for a specific node space
    nimbusRef = mat.GetNimbusRef(nodespaceId)
    if nimbusRef is None:
        raise ValueError("Cannot retrieve the nimbus ref for that node space")

    # Retrieve the graph corresponding to that node space
    graph = nimbusRef.GetGraph()
    if graph is None:
        raise ValueError("Cannot retrieve the graph of this nimbus ref")

    # Retrieve the end node of this graph
    endNodePath = nimbusRef.GetPath(maxon.NIMBUS_PATH.MATERIALENDNODE)

    # Solo the end node
    nimbusRef.SetPath(maxon.NIMBUS_PATH.SOLO, endNodePath)

    # Retrieve the solo node of this graph
    soloNodePath = nodeMaterial.GetSoloNodePath(nodespaceId)

    print(endNodePath == soloNodePath)

    # Insert the material In the document
    doc.InsertMaterial(mat)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
