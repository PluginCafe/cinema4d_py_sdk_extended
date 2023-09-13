#coding: utf-8
"""Demonstrates creating new node materials and adding graphs to them.

See the `create_redshift_nodematerial` and `create_standard_nodematerial` examples in this directory
for also populating a graph with nodes and connecting them.

Topics:
    * Creating node materials.
    * Adding and removing graphs to them.
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
    # Node materials are instances of the classic API material type #BaseMaterial. The node data
    # is attached to them as a #NodeMaterial. We can retrieve a #NodeMaterial instance for each 
    # #BaseMaterial instance, whether or not this material actually is a node material or not.

    # Instantiate a classic API material.
    material: c4d.BaseMaterial = c4d.BaseMaterial(c4d.Mmaterial)
    if not material:
        raise MemoryError(f"{material = }")
    doc.InsertMaterial(material)

    # Get the node material for it and add a graph for the currently active material space to it. 
    nodeMaterial: c4d.NodeMaterial = material.GetNodeMaterialReference()
    graph: maxon.GraphModelInterface = nodeMaterial.CreateDefaultGraph(c4d.GetActiveNodeSpaceId())
    if graph.IsNullValue():
        raise RuntimeError("Could not add graph to material.")
    
    # The method #CreateDefaultGraph we used above does not create an empty graph, but the setup
    # the respective node space considers to be its default setup. For Redshift this is for example
    # an RS Standard Material node connected to an Output end node.
    print ("Nodes in CreateDefaultGraph setup:")
    for node in graph.GetRoot().GetInnerNodes(mask=maxon.NODE_KIND.NODE, includeThis=False):
        print (f"{node}")

    # Remove the graph we just created.
    nodeMaterial.RemoveGraph(c4d.GetActiveNodeSpaceId())

    # We can also create an empty graph which contains no nodes at all with. 
    graph: maxon.GraphModelInterface = nodeMaterial.CreateEmptyGraph(c4d.GetActiveNodeSpaceId())
    if graph.IsNullValue():
        raise RuntimeError("Could not add graph to material.")

    print ("Nodes in CreateEmptyGraph setup:")
    for node in graph.GetRoot().GetInnerNodes(mask=maxon.NODE_KIND.NODE, includeThis=False):
        print (f"{node}")

    # Remove the graph again.
    nodeMaterial.RemoveGraph(c4d.GetActiveNodeSpaceId())

    # Finally, we should be aware that node material can hold graphs for multiple node spaces and
    # therefore can be used with multiple render engines. To do this, we can simply add multiple
    # graphs for specific nodes spaces.

    # Add a default graph for both the Redshift and Standard material node space, check the "Basic"
    # tab of the material, it will list a graph for both spaces. When you switch between render 
    # engines, the material will have its own graph for each engine. To support 3rd party render
    # engines, you must ask their vendor for their node space ID.
    nodeMaterial.CreateDefaultGraph("com.redshift3d.redshift4c4d.class.nodespace")
    nodeMaterial.CreateDefaultGraph("net.maxon.nodespace.standard")


if __name__ == "__main__":
    main()
