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
__date__ = "04/06/2024"
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
    idOutputNode: maxon.Id = maxon.Id("com.redshift3d.redshift4c4d.node.output")
    idStandardMaterial: maxon.Id = maxon.Id("com.redshift3d.redshift4c4d.nodes.core.standardmaterial")
    idTextureNode: maxon.Id = maxon.Id("com.redshift3d.redshift4c4d.nodes.core.texturesampler")
    idMixNode: maxon.Id = maxon.Id("com.redshift3d.redshift4c4d.nodes.core.rscolormix")

    # Instantiate a material, get its node material, and add a graph for the RS material space.
    material: c4d.BaseMaterial = c4d.BaseMaterial(c4d.Mmaterial)
    if not material:
        raise MemoryError(f"{material = }")

    nodeMaterial: c4d.NodeMaterial = material.GetNodeMaterialReference()
    redshiftNodeSpaceId: maxon.Id =  maxon.Id("com.redshift3d.redshift4c4d.class.nodespace")
    graph: maxon.GraphModelRef = nodeMaterial.CreateEmptyGraph(redshiftNodeSpaceId)
    if graph.IsNullValue():
        raise RuntimeError("Could not add Redshift graph to material.")

    # Open an undo operation and insert the material into the document. We must do this before we 
    # modify the graph of the material, as otherwise the viewport material will not correctly display 
    # the textures of the material until the user manually refreshes the material. It is also 
    # important to insert the material after we added the default graph to it, as otherwise we will 
    # end up with two undo steps in the undo stack.
    if not doc.StartUndo():
        raise RuntimeError("Could not start undo stack.")
    
    doc.InsertMaterial(material)
    if not doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, material):
        raise RuntimeError("Could not add undo item.")

    # Define the user data for the transaction. This is optional, but can be used to tell the Nodes
    # API to add the transaction to the current undo stack instead of creating a new one. This will
    # then have the result that adding the material, adding the graph, and adding the nodes will be
    # one undo step in the undo stack.
    userData: maxon.DataDictionary = maxon.DataDictionary()
    userData.Set(maxon.nodes.UndoMode, maxon.nodes.UNDO_MODE.ADD)

    # Start modifying the graph by opening a transaction. Node graphs follow a database like 
    # transaction model where all changes are only finally applied once a transaction is committed.
    with graph.BeginTransaction(userData) as transaction:

        # Add the output, i.e., the terminal end node of the graph, as well as a standard material
        # node to the graph.
        outNode: maxon.GraphNode = graph.AddChild(maxon.Id(), idOutputNode)
        materialNode: maxon.GraphNode = graph.AddChild(maxon.Id(), idStandardMaterial)

        # Add two texture nodes and a blend node to the graph.
        rustTexNode: maxon.GraphNode = graph.AddChild(maxon.Id(), idTextureNode)
        sketchTexNode: maxon.GraphNode = graph.AddChild(maxon.Id(), idTextureNode)
        mixNode: maxon.GraphNode = graph.AddChild(maxon.Id(), idMixNode)

        # Get the input 'Surface' port of the 'Output' node and the output 'Out Color' port of the
        # 'Standard Material' node and connect them.
        surfacePortOutNode: maxon.GraphNode = outNode.GetInputs().FindChild(
            "com.redshift3d.redshift4c4d.node.output.surface")
        outcolorPortMaterialNode: maxon.GraphNode = materialNode.GetOutputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.standardmaterial.outcolor")
        outcolorPortMaterialNode.Connect(surfacePortOutNode)

        # Set the default value of the 'Mix Amount' port, i.e., the value the port has when no 
        # wire is connected to it. This is equivalent to the user setting the value to "0.5" in 
        # the Attribute Manager.
        mixAmount: maxon.GraphNode = mixNode.GetInputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.rscolormix.mixamount")
        mixAmount.SetPortValue(0.5)

        # Set the path sub ports of the 'File' ports of the two image nodes to the texture URLs 
        # established above. Other than for the standard node space image node, the texture is 
        # expressed as a port bundle, i.e., a port which holds other ports. The texture of a texture
        # node is expressed as the "File" port, of which "Path", the URL, is only one of the possible
        # sub-ports to set.
        pathRustPort: maxon.GraphNode = rustTexNode.GetInputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.texturesampler.tex0").FindChild("path")
        pathSketchPort: maxon.GraphNode = sketchTexNode.GetInputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.texturesampler.tex0").FindChild("path")
        pathRustPort.SetPortValue(urlTexRust)
        pathSketchPort.SetPortValue(urlTexSketch)

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
        stdBaseColorInPort: maxon.GraphNode = materialNode.GetInputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.standardmaterial.base_color")

        # Wire up the two texture nodes to the blend node and the blend node to the BSDF node.
        rustTexColorOutPort.Connect(mixInput1Port, modes=maxon.WIRE_MODE.NORMAL, reverse=False)
        sketchTexColorOutPort.Connect(mixInput2Port, modes=maxon.WIRE_MODE.NORMAL, reverse=False)
        mixColorOutPort.Connect(stdBaseColorInPort, modes=maxon.WIRE_MODE.NORMAL, reverse=False)

        # Finish the transaction to apply the changes to the graph.
        transaction.Commit()

    if not doc.EndUndo():
        raise RuntimeError("Could not end undo stack.")

    c4d.EventAdd()
    
if __name__ == "__main__":
    main()