#coding: utf-8
"""Demonstrates accessing node materials and their graph contents in a scene.

Topics:
    * Accessing node materials in a document.
    * Testing for and accessing graphs for node spaces in a node material.
    * Iterating over nodes in a graph.
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2023 MAXON Computer GmbH"
__date__ = "01/09/2023"
__license__ = "Apache-2.0 License"
__version__ = "2024.0.0"


import c4d
import maxon

doc: c4d.documents.BaseDocument # The active document.

def main():
    """
    """
    # Node materials are instances of the Cinema API material type #BaseMaterial. The node data
    # is attached to them as a #NodeMaterial. We can retrieve a #NodeMaterial instance for each 
    # #BaseMaterial instance, whether or not this material actually is a node material or not.
    # Because of that, we must iterate over all material in a document to find node materials and 
    # retrieve the #NodeMaterial for each of them.

    # For each #material in the currently active document get its #nodeMaterial reference.
    material: c4d.BaseMaterial
    for material in doc.GetMaterials():
        nodeMaterial: c4d.NodeMaterial = material.GetNodeMaterialReference()
    
        # To test if a material has a graph for a specific space, we must use the method #HasSpace. 
        # To support 3rd party render engines, you must ask them for their node space ID.
        for nid in ("net.maxon.nodespace.standard",                 # Standard Renderer
                    "com.redshift3d.redshift4c4d.class.nodespace"): # Redshift Renderer
            if not nodeMaterial.HasSpace(nid):
                continue
            
            # This material has a graph for the space #nid, we retrieve it.
            graph: maxon.GraphModelInterface = nodeMaterial.GetGraph(nid)
            if graph.IsNullValue():
                raise RuntimeError("Found malformed empty graph associated with node space.")
            
            # Now we iterate over all items in the graph.
            print (f"\nThe material '{material.GetName()}' has a graph in the node space '{nid}'.")
            root: maxon.GraphNode = graph.GetViewRoot()

            # Iterate over the direct children of the graph root.
            node: maxon.GraphNode
            for node in root.GetChildren():
                print (f"\tDirect child of graph root: {node.GetId()}")
            
            print ("\t" + "-" * 60)
            # Iterate over all nodes in the graph, i.e., unpack things like nodes nested in groups. 
            # With the mask argument we could also include ports in this iteration.
            for node in root.GetInnerNodes(mask=maxon.NODE_KIND.NODE, includeThis=False):
                print (f"\tNode in the graph: {node}")
            
    c4d.EventAdd()


if __name__ == "__main__":
    main()
