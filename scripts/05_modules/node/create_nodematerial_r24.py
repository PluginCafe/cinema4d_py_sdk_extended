"""
Copyright: MAXON Computer GmbH
Author: Manuel Magalhaes

Description:
    Creates a NodeMaterial for the current node space and for Redshift node 
    space. 

    NodeMaterials inherit from BaseMaterial. To be able to use the functions 
    that are in the NodeMaterial class, the BaseMaterial must be cast to a 
    NodeMaterial. This is done with the function GetNodeMaterialReference. To 
    add a graph to an existing node space, one must use the function AddGraph.
    If one wants to have access to an already added node graph, one must 
    retrieve the nimbus reference which does store the graph. Once one has 
    retrieved the graph, one can access the root that contains all the nodes.
    
Class/method highlighted:
    - GetNodeMaterialReference
    - AddGraph
    - GetActiveNodeSpaceId
    - GetChildren
    - GetNimbusRef
"""
import c4d
import maxon
import maxon.frameworks.nodespace
import maxon.frameworks.nodes

# Define a function that will create the node material for the passed
# nodespace Id and return the root of the created Graph


def CreateMaterialForNodeSpace(nodespaceId):
    # Create a baseMaterial first
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    if mat is None:
        raise ValueError("Cannot create a BaseMaterial.")

    # Retrieve the reference of the material as a node material.
    nodeMaterial = mat.GetNodeMaterialReference()
    if nodeMaterial is None:
        raise ValueError("Cannot retrieve nodeMaterial reference.")

    # Add a graph for the space Id
    addedGraph = nodeMaterial.AddGraph(nodespaceId)
    if addedGraph is None:
        raise ValueError("Cannot add a GraphNode for this NodeSpace.")

    # Retrieve the Nimbus reference for a specific NodeSpace
    nimbusRef = mat.GetNimbusRef(nodespaceId)
    if nimbusRef is None:
        raise ValueError(
            "Cannot retrieve the nimbus reference for that NodeSpace.")

    # Retrieve the graph corresponding to that NodeSpace.
    graph = nimbusRef.GetGraph()
    if graph is None:
        raise ValueError("Cannot retrieve the graph of this nimbus NodeSpace.")

    # Retrieve the root of the graph
    root = graph.GetRoot()

    # Insert the material in the document
    doc.InsertMaterial(mat)
    return root


# Define a function that will recursively print all the child of the root node.
def PrintChildren(node):
    if node is None:
        return None
    # Print the current Node
    print(node)

    # Call GetChildren on this node with the delegate function
    node.GetChildren(PrintChildren, maxon.frameworks.graph.NODE_KIND.ALL_MASK)

    # Important that the delegate return True or False
    return True


def main():

    # Retrieve the current node space Id
    nodespaceId = c4d.GetActiveNodeSpaceId()

    # Create the material and retrieve the root of the graph
    root = CreateMaterialForNodeSpace(nodespaceId)

    # Start the recursive process on the first node
    PrintChildren(root)

    # Do the same with the Redshift node space. The Redshift plugin is not 
    # installed by default, so we call the function in an exception handling
    # context.
    redShiftNodeSpPaceId = maxon.Id(
        'com.redshift3d.redshift4c4d.class.nodespace')
    try:
        root = CreateMaterialForNodeSpace(redShiftNodeSpPaceId)
        PrintChildren(root)
    except:
        print(f"The node space with id {redShiftNodeSpPaceId} does not exist")

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
