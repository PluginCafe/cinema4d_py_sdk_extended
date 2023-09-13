#coding: utf-8
"""Demonstrates setting up a Standard renderer node material composed out of multiple nodes.

Creates a new node material with a graph in the standard material space, containing two texture 
nodes and a blend node, in addition to the default BSDF and material node of the material.

Topics:
    * Creating a node material and adding a graph
    * Adding nodes to a graph
    * Setting the value of ports without wires
    * Connecting ports with a wires

Change Notes:
    01/09/2023: Updated script to align better with new create_redshift_material_2024.py for 2924.0
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2023 MAXON Computer GmbH"
__date__ = "09/01/2023"
__license__ = "Apache-2.0 License"
__version__ = "2023.1.0"


import c4d
import maxon

doc: c4d.documents.BaseDocument # The active document.

def main() -> None:
    """Runs the example.
    """
    # The asset URLs for the "RustPaint0291_M.jpg" and "Sketch (HR basic026).jpg" texture assets in 
    # "tex/Surfaces/Dirt Scratches & Smudges/". These could also be replaced with local texture URLs,
    # e.g., "file:///c:/textures/stone.jpg". These IDs can be discovered with the #-button in the info
    # area of the Asset Browser.
    urlTexRust: maxon.Url = maxon.Url(r"asset:///file_edb3eb584c0d905c")
    urlTexSketch: maxon.Url = maxon.Url(r"asset:///file_3b194acc5a745a2c")

    # The node asset IDs for the two node types to be added in the example; the image node and the
    # blend node. These and all other node IDs can be discovered in the node info overlay in the 
    # bottom left corner of the Node Editor. Open the Cinema 4D preferences by pressing CTRL/CMD + E
    # and enable Node Editor -> Ids in order to see node and port IDs in the Node Editor.
    idImageNode: maxon.Id = maxon.Id("net.maxon.pattern.node.generator.image")
    idBlendNode: maxon.Id = maxon.Id("net.maxon.pattern.node.effect.blend")

    # Instantiate a material, get its node material and the graph for the standard material space.
    material: c4d.BaseMaterial = c4d.BaseMaterial(c4d.Mmaterial)
    if not material:
        raise MemoryError(f"{material = }")

    nodeMaterial: c4d.NodeMaterial = material.GetNodeMaterialReference()
    graph: maxon.GraphModelRef = nodeMaterial.CreateDefaultGraph(maxon.Id("net.maxon.nodespace.standard"))
    if graph.IsNullValue():
        raise RuntimeError("Could not add standard graph to material.")

    # Attempt to find the BSDF node contained in the default graph setup.
    result: list[maxon.GraphNode] = []
    maxon.GraphModelHelper.FindNodesByAssetId(
        graph, maxon.Id("net.maxon.render.node.bsdf"), True, result)
    if len(result) < 1:
        raise RuntimeError("Could not find BSDF node in material.")
    bsdfNode: maxon.GraphNode = result[0]

    # Start modifying the graph by opening a transaction. Node graphs follow a database like 
    # transaction model where all changes are only finally applied once a transaction is committed.
    with graph.BeginTransaction() as transaction:
        # Add two texture nodes and a blend node to the graph.
        rustImgNode: maxon.GraphNode = graph.AddChild(maxon.Id(), idImageNode)
        sketchImgNode: maxon.GraphNode = graph.AddChild(maxon.Id(), idImageNode)
        blendNode: maxon.GraphNode = graph.AddChild(maxon.Id(), idBlendNode)

        # Set the default value of the 'Blend Mode' port, i.e., the value the port has when no 
        # wire is connected to it. This is equivalent to the user setting the value to "Darken" in 
        # the Attribute Manager.
        blendPort: maxon.GraphNode = blendNode.GetInputs().FindChild("blendmode")
        blendPort.SetDefaultValue(maxon.Id("net.maxon.render.blendmode.darken"))

        # Set the 'File' ports of the two image nodes to the texture URLs established above.
        urlRustTexPort: maxon.GraphNode = rustImgNode.GetInputs().FindChild("url")
        urlSketchTexPort: maxon.GraphNode = sketchImgNode.GetInputs().FindChild("url")
        urlRustTexPort.SetDefaultValue(urlTexRust)
        urlSketchTexPort.SetDefaultValue(urlTexSketch)

        # Get the color output ports of the two texture nodes and the color blend node.
        rustTexColorOutPort: maxon.GraphNode = rustImgNode.GetOutputs().FindChild("result")
        sketchTexColorOutPort: maxon.GraphNode = sketchImgNode.GetOutputs().FindChild("result")
        blendColorOutPort: maxon.GraphNode = blendNode.GetOutputs().FindChild("result")

        # Get the fore- and background port of the blend node and the color port of the BSDF node.
        blendForegroundInPort: maxon.GraphNode = blendNode.GetInputs().FindChild("foreground")
        blendBackgroundInPort: maxon.GraphNode = blendNode.GetInputs().FindChild("background")
        bsdfColorInPort: maxon.GraphNode = bsdfNode.GetInputs().FindChild("color")

        # Wire up the two texture nodes to the blend node and the blend node to the BSDF node.
        rustTexColorOutPort.Connect(blendForegroundInPort, modes=maxon.WIRE_MODE.NORMAL, reverse=False)
        sketchTexColorOutPort.Connect(blendBackgroundInPort, modes=maxon.WIRE_MODE.NORMAL, reverse=False)
        blendColorOutPort.Connect(bsdfColorInPort, modes=maxon.WIRE_MODE.NORMAL, reverse=False)

        # Finish the transaction to apply the changes to the graph.
        transaction.Commit()

    # Insert the material into the document and push an update event.
    doc.InsertMaterial(material)
    c4d.EventAdd()
    
if __name__ == "__main__":
    main()