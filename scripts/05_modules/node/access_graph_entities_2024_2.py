#coding: utf-8
"""Demonstrates the inner structure of node graphs and how to find entities in them.

Run this script in the Script Manager on a document which contains at least one Redshift node 
material with at least one "Texture" node in the graph. The script will print out the URL of 
each texture node and print the GraphNode tree for each material in the document.

Topics:
    * The inner structure of a graph.
    * The difference between node and asset IDs.
    * Reading the value of a port (both for connected and unconnected ports).

Entities:
    * PrintGraphTree: Prints a given graph as a GraphNode tree to the console.
    * main: Runs the main example.
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2023 MAXON Computer GmbH"
__date__ = "16/11/2023"
__license__ = "Apache-2.0 License"
__version__ = "2024.2.0"


import c4d
import maxon
import typing

doc: c4d.documents.BaseDocument # The active document.

def PrintGraphTree(graph: maxon.GraphModelRef) -> None:
    """Prints a given graph as a GraphNode tree to the console.

    This can be helpful to understand the structure of a graph. Note that this will print the true
    data of a graph, which will include all ports (most of them are usually hidden in the Node 
    Editor) and also other hidden graph entities.
    """
    kindMap: dict[int, str] = {
        maxon.NODE_KIND.NODE: "NODE",
        maxon.NODE_KIND.INPORT: "INPORT",
        maxon.NODE_KIND.INPUTS: "INPUTS",
        maxon.NODE_KIND.NONE: "NONE",
        maxon.NODE_KIND.OUTPORT: "OUTPORT",
        maxon.NODE_KIND.OUTPUTS: "OUTPUTS",
    }
    if graph.IsNullValue():
        raise RuntimeError("Invalid graph.")
    
    def iterTree(node: maxon.GraphNode, 
                 depth: int = 0) -> typing.Iterator[tuple[int, maxon.GraphNode]]:
        """Yields all descendants of #node and their hierarchy depth, including #node itself.

        This is one way to iterate over a node graph. But when one does not require the hierarchy
        as we do here, one should use GraphNode.GetInnerNodes() as demonstrated in main() below.
        """
        yield (node, depth)
        for child in node.GetChildren():
            for item in iterTree(child, depth + 1):
                yield item
    
    root: maxon.GraphNode = graph.GetRoot()
    for node, depth in iterTree(root):
        print (f"{'  ' * depth} + '{node.GetId()}' [{kindMap.get(node.GetKind(), 'UNKNOWN KIND')}]"+
               ("" if not node.GetId().IsEmpty() else f"(Root Node)"))



def main():
    """Runs the main example.
    """
    # For each #material in the currently active document ...
    for material in doc.GetMaterials():
        # ... get its node material reference and step over all materials which do not have a 
        # Redshift graph or where the graph is malformed.
        nodeMaterial: c4d.NodeMaterial = material.GetNodeMaterialReference()
        if not nodeMaterial.HasSpace("com.redshift3d.redshift4c4d.class.nodespace"):
            continue

        graph: maxon.GraphModelRef = nodeMaterial.GetGraph(
            "com.redshift3d.redshift4c4d.class.nodespace")
        if graph.IsNullValue():
            raise RuntimeError("Found malformed empty graph associated with node space.")
        
        # Get the root of the graph, the node which contains all other nodes. Since we only want 
        # to read information here, we do not need a graph transaction. But for all write operations
        # we would have to start a transaction on #graph.
        root: maxon.GraphNode = graph.GetRoot()

        # Iterate over all nodes in the graph, i.e., unpack things like nodes nested in groups. 
        # With the mask argument we could also include ports in this iteration.
        for node in root.GetInnerNodes(mask=maxon.NODE_KIND.NODE, includeThis=False):
            
            # There is a difference between the asset ID of a node and its ID. The asset ID is
            # the identifier of the node template asset from which a node has been instantiated.
            # It is more or less the node type identifier. When we have three RS Texture nodes
            # in a graph they will all have the same asset ID. But their node ID on the other hand
            # will always be unique to a node.
            assetId: maxon.Id = node.GetValue("net.maxon.node.attribute.assetid")[0]
            nodeId: maxon.Id = node.GetId()

            # Step over everything that is not a Texture node, we could also check here for a node
            # id, in case we want to target a specific node instance.
            if assetId != maxon.Id("com.redshift3d.redshift4c4d.nodes.core.texturesampler"):
                continue

            # Now we got hold of a Texture node in a graph. To access a port value on this node,
            # for example the value of the Filename.Path port, we must get hold of the port entity. 

            # Get the Filename input port of the Texture node.
            filenameInPort: maxon.GraphNode = node.GetInputs().FindChild(
                "com.redshift3d.redshift4c4d.nodes.core.texturesampler.tex0")
            
            # But #filenameInPort is a port bundle - that is how ports are called which are composed
            # of multiple (static) child ports. The port has the data type "Filename" with which we 
            # cannot do much on its own. Just as in the node editor, we must use its nested child 
            # ports to get and set values, in this case the "path".
            pathPort: maxon.GraphNode = filenameInPort.FindChild("path")

            # Another way to get hold of the path port would be using a node path, where we define
            # an identifier which addresses the port node directly from the root of the graph.
            alsoPathPort: maxon.GraphNode = graph.GetNode(
                node.GetPath() + ">com.redshift3d.redshift4c4d.nodes.core.texturesampler.tex0\path")
            
            # The underlying information is here the nature of the type GraphNode. The word "node"
            # in it does not refer to a node in a graph but to a node in a tree. All entities in a
            # graph - nodes, ports, and things that are not obvious from the outside - are organized
            # in a tree of GraphNode instances. Each GraphNode instance has then a NODEKIND which
            # expresses the purpose of that node, examples for node kinds are:
            #
            #    * NODE_KIND.NODE   : A GraphNode that represents a tangible node in a graph. The
            #                          Nodes API calls this a 'true node'.
            #    * NODE_KIND.INPORT : A GraphNode that represents a input port in a graph.
            #    * NODE_KIND.OUTPORT: A GraphNode that represents a output port in a graph.
            #
            # For our example the GraphNode tree of a material graph could look like this:

            # + ""                                          // The root node of the graph, it is
            # |                                                is the container that holds all 
            # |                                                entities in the graph. It has the
            # |                                                empty ID as its ID.
            # |---+ "texturesampler@bbRMv5CAGpPtJFHs5n43CV" // An RS Texture node in it.
            # |   |---+ ">"                                 // A child node of the texture that 
            # |       |                                        holds all of its input ports, it has
            # |       |                                        a special NODE_KIND and is the 
            # |       |                                        underlying node of what we accessed 
            # |       |                                        with the .GetInputs() call above.
            # |       |---+ "...core.texturesampler.tex0"   // The Filename input port of a Texture 
            # |           |                                    node. It is a port bundle and 
            # |           |                                    therefore has child ports attached to
            # |           |                                    it. This node and all of its children
            # |           |                                    are of type NODE_KIND.INPORT.
            # |           |---+ "path"                      // The nested port for the Filename.Path.
            # |---+ "standardmaterial@FTf3YdB7AxEn1JKQL2$W" // An RS Standard Material node in the
            # |   |                                            graph. 
            # |   |---+ ">"                                 // Its input ports. 
            # |   |   |  ...
            # |   |
            # |   |---+ "<"                                 // Its output ports. 
            # |       |  ...
            # |
            # |---+ ...                                     // Another node in the graph.

            # On this entity we can now read and write values. In 2023 and earlier we would have
            # used GetDefaultValue for this, in 2024 and onward these methods have been 
            # deprecated and we use GetValue now instead.
            url: str | None = pathPort.GetValue("effectivevalue")

            print (f"{pathPort}: {url}")
        
        # Print the GraphNode tree for the current #graph. 
        PrintGraphTree(graph)


if __name__ == "__main__":
    main()