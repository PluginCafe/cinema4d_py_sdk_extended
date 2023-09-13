#coding: utf-8
"""Demonstrates setting up a Redshift node material composed out of multiple nodes.

Creates a new node material with a graph in the Redshift material space, containing two texture 
nodes and a mix node, in addition to the default RS Standard Material and Output node of the 
material.

Topics:
    * Creating a node material and adding a graph.
    * Adding nodes to a graph.
    * Setting the value of ports without wires.
    * Connecting ports with a wires.
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2023 MAXON Computer GmbH"
__date__ = "01/09/2023"
__license__ = "Apache-2.0 License"
__version__ = "2024.0.0"


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

    # The node asset IDs for the two node types to be added in the example; the texture node and the
    # mix node. These and all other node IDs can be discovered in the node info overlay in the 
    # bottom left corner of the Node Editor. Open the Cinema 4D preferences by pressing CTRL/CMD + E
    # and enable Node Editor -> Ids in order to see node and port IDs in the Node Editor.
    idTextureNode: maxon.Id = maxon.Id("com.redshift3d.redshift4c4d.nodes.core.texturesampler")
    idMixNode: maxon.Id = maxon.Id("com.redshift3d.redshift4c4d.nodes.core.rscolormix")
    idRsStandardMaterial: maxon.Id = maxon.Id("com.redshift3d.redshift4c4d.nodes.core.standardmaterial")

    # Instantiate a material, get its node material and the graph for the RS material space.
    material: c4d.BaseMaterial = c4d.BaseMaterial(c4d.Mmaterial)
    if not material:
        raise MemoryError(f"{material = }")

    nodeMaterial: c4d.NodeMaterial = material.GetNodeMaterialReference()
    graph: maxon.GraphModelRef = nodeMaterial.CreateDefaultGraph(
        maxon.Id("com.redshift3d.redshift4c4d.class.nodespace"))
    if graph.IsNullValue():
        raise RuntimeError("Could not add RS graph to material.")

    doc.InsertMaterial(material)
    c4d.EventAdd()

    # Attempt to find the core material node contained in the default graph setup.
    result: list[maxon.GraphNode] = []
    maxon.GraphModelHelper.FindNodesByAssetId(graph, idRsStandardMaterial, True, result)
    if len(result) < 1:
        raise RuntimeError("Could not find RS Standard node in material.")
    standardNode: maxon.GraphNode = result[0]

    # Start modifying the graph by opening a transaction. Node graphs follow a database like 
    # transaction model where all changes are only finally applied once a transaction is committed.
    with graph.BeginTransaction() as transaction:
        # Add two texture nodes and a blend node to the graph.
        rustTexNode: maxon.GraphNode = graph.AddChild(maxon.Id(), idTextureNode)
        sketchTexNode: maxon.GraphNode = graph.AddChild(maxon.Id(), idTextureNode)
        mixNode: maxon.GraphNode = graph.AddChild(maxon.Id(), idMixNode)

        # Set the default value of the 'Mix Amount' port, i.e., the value the port has when no 
        # wire is connected to it. This is equivalent to the user setting the value to "0.5" in 
        # the Attribute Manager.
        mixAmount: maxon.GraphNode = mixNode.GetInputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.rscolormix.mixamount")
        mixAmount.SetDefaultValue(0.5)

        # Set the path sub ports of the 'File' ports of the two image nodes to the texture URLs 
        # established above. Other than for the standard node space image node, the texture is 
        # expressed as a port bundle, i.e., a port which holds other ports. The texture of a texture
        # node is expressed as the "File" port, of which "Path", the URL, is only one of the possible
        # sub-ports to set.
        pathRustPort: maxon.GraphNode = rustTexNode.GetInputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.texturesampler.tex0").FindChild("path")
        pathSketchPort: maxon.GraphNode = sketchTexNode.GetInputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.texturesampler.tex0").FindChild("path")
        pathRustPort.SetDefaultValue(urlTexRust)
        pathSketchPort.SetDefaultValue(urlTexSketch)

        # Get the color output ports of the two texture nodes and the color blend node.
        rustTexColorOutPort: maxon.GraphNode = rustTexNode.GetOutputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.texturesampler.outcolor")
        sketchTexColorOutPort: maxon.GraphNode = sketchTexNode.GetOutputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.texturesampler.outcolor")
        mixColorOutPort: maxon.GraphNode = mixNode.GetOutputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.rscolormix.outcolor")

        # Get the fore- and background port of the blend node and the color port of the BSDF node.
        mixInput1Port: maxon.GraphNode = mixNode.GetInputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.rscolormix.input1")
        mixInput2Port: maxon.GraphNode = mixNode.GetInputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.rscolormix.input2")
        stdBaseColorInPort: maxon.GraphNode = standardNode.GetInputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.standardmaterial.base_color")

        # Wire up the two texture nodes to the blend node and the blend node to the BSDF node.
        rustTexColorOutPort.Connect(mixInput1Port, modes=maxon.WIRE_MODE.NORMAL, reverse=False)
        sketchTexColorOutPort.Connect(mixInput2Port, modes=maxon.WIRE_MODE.NORMAL, reverse=False)
        mixColorOutPort.Connect(stdBaseColorInPort, modes=maxon.WIRE_MODE.NORMAL, reverse=False)

        # Finish the transaction to apply the changes to the graph.
        transaction.Commit()

    # Insert the material into the document and push an update event.
    doc.InsertMaterial(material)
    c4d.EventAdd()
    
if __name__ == "__main__":
    main()