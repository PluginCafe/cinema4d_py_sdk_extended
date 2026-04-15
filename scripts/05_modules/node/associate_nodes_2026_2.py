"""Demonstrates how to associate nodes in a Maxon API graph with their corresponding Cinema 4D API 
surrogate elements.

Cinema 4D is split into two major APIs:

- *Cinema API*: The 'classic' API that represents and describes most tangible entities in Cinema 4D,
   such as materials, objects, tags, and so on. This API is mostly based on the concept of
   `BaseList2D` scene elements that hold data containers and are organized in hierarchical
   and generic node relationships (via `GeListNode`, one of the base classes of `BaseList2D`). I.e.,
   this data forms the graph that makes up a Cinema 4D scene.
- *Maxon API*: The Maxon API is a more modern API that also includes the Nodes API, which offers a
   a new (but not drop-in replacement) way to represent nodal scene data. It is used for Scene and
   Material Nodes at the moment (and subject of this part of the documentation).

But the majority of the UI of Cinema 4D is still based on the Cinema API, and the Attribute Manager
for example can only display `BaseList2D` scene elements and not `GraphNode` entities of the Maxon 
API. So, for user interaction purposes, Maxon API nodes must be associated with Cinema API surrogate
scene elements that represent those nodes in the Cinema API world.

A `NimusBaseInterface` is the glue between a Cinema API scene element and a Maxon API node graph. It 
not only provides access to the actual Nodes API graph associated with that element, but also 
manages the association between Nodes API nodes/ports and their Cinema API surrogate elements.

This example focuses on the Scene Nodes system, but the same principles apply to other Maxon API 
node graphs.

Compatibility Note: 

    Remove all code in #main up to `print("\n\n--- Maxon API Scene Nodes Data ---\n") and the 
    #mxutils import statement to make this example run in older versions of Cinema 4D (should work 
    at least in 2025.x and with minor modifications even in 2024.x).
    
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2026 MAXON Computer GmbH"
__date__ = "05/01/2026"
__license__ = "Apache-2.0 License"
__version__ = "2026.0.0"

import c4d
import maxon
import mxutils

doc: c4d.documents.BaseDocument  # The currently active document.
op: c4d.BaseObject | None  # The primary selected object in `doc`. Can be `None`.

def main() -> None:
    """Called by Cinema 4D when the script is being executed.
    """
    # An good way to visualize what we are doing is mxutils.GetSceneGraphString, as it will give
    # us a visual representation of a Cinema API scene graph. We can find there the nodes we
    # will retrieve and associate with Maxon API nodes further below. You have to look for a 
    # Scene Nodes scene hook in the output. It will also hold all surrogate nodes for the Maxon
    # API Scene Nodes graph of the document.
    print("--- Cinema API Scene Graph ---\n")
    c4d.ClearPythonConsole()
    print(mxutils.GetSceneGraphString(doc))

    print("\n\n--- Maxon API Scene Nodes Data ---\n")

    # Now we attempt to get the Cinema API scene element to which the Scene Nodes system of a 
    # document is tied (and which also physically holds all Cinema API surrogate nodes for the
    # Maxon API Scene Nodes graph of the document). For scene nodes, this is a scene hook, for
    # material graphs it would be a BaseMaterial.
    # 
    # Scene hooks are a Cinema API node type for which always exactly one instance exists per 
    # document. It is only a coincidence that they also use the term "scene" in their name, there 
    # is no semantic relation between scene hooks and Scene Nodes. For material graphs, we would 
    # for example call `FindNimbusRef` on the `BaseMaterial` instance instead of retrieving 
    # a scene hook.
    hook: c4d.BaseList2D = doc.FindSceneHook(c4d.SCENENODES_IDS_SCENEHOOK_ID)
    if not hook:
        raise RuntimeError("Could not retrieve Scene Nodes scene hook.")

    # A `BaseList2D` offers various methods to retrieve `NimusBaseInterface` references for itself.
    # And a NimusBaseInterface is the glue between a Cinema API scene element and a Maxon API node 
    # graph. Here is the connection being made between a Cinema API scene element in form of a
    # scene hook and the the Scene Nodes Maxon API graph that is associated with that scene hook. 
    # Scene nodes come with the special condition that the their graph might not yet exist for 
    # performance reasons, so we must always send #MSG_CREATE_IF_REQUIRED before attempting to
    # access a scene nodes graph. For a material node graph, this would not be necessary.
    hook.Message(maxon.neutron.MSG_CREATE_IF_REQUIRED)
    handler: maxon.NimbusBaseRef | None = hook.GetNimbusRef(maxon.NodeSpaceIdentifiers.SceneNodes)
    if not handler:
        raise RuntimeError("Could not retrieve Scene Nodes handler.")

    # Now we get the nodes graph that is associated with this nimbus handler and iterate over all 
    # true nodes in it. The Nodes API follows the a bit odd notion that it represents graphs as 
    # trees of entities, where each entity is a  GraphNode. Some of those entities are 'true' nodes,
    # i.e., nodes that also an end user would see in the Node Editor, while other entities represent
    # things like input and output ports (but are also GraphNodes). So, in short, a GraphNode does
    # not necessarily represent a 'true' node.
    graph: maxon.NodesGraphModelRef = handler.GetGraph()
    root: maxon.GraphNode = graph.GetViewRoot()
    
    # For each entity in the graph...
    for entity in root.GetInnerNodes(maxon.NODE_KIND.ALL_MASK, False, None):
        # .. step over all non 'true node' entities ...
        if entity.GetKind() != maxon.NODE_KIND.NODE:
            continue

        # .. and find (or create) the BaseList2D Cinema API surrogate entity that represents the 
        # current #entity in this Maxon API graph. This is the surrogate that is shown in an 
        # Attribute Manager when the user selects the node in the Node Editor. Reading and writing
        # its parameters will be reflected in the Maxon API node and vice versa.
        surrogate: c4d.BaseList2D = handler.FindOrCreateCorrespondingBaseList(entity.GetPath())
        print(f"Maxon API node: {entity.GetPath()} -> Cinema API surrogate node: {surrogate}")

        # Now we are going to iterate over all input ports of #entity and translate them into
        # parameter IDs for our #surrogate.
        for port in entity.GetInnerNodes(maxon.NODE_KIND.ALL_MASK, False, None):
            if port.GetKind() != maxon.NODE_KIND.INPORT:
                continue

            # The reasons why we use here a try/except block is because nodes tend to hold input
            # ports which only fulfill internal purposes and do not have a corresponding parameter
            # in the Cinema API surrogate node (ports without an UI). Getting the DescID for such 
            # ports will fail with a ValueError because ports without an UI are not translated (and 
            # we are also probably not interested in them here).
            try:
                did: c4d.DescID = handler.GetDescID(port.GetPath()) # This fails
                print(f"\tInput port: {port.GetPath()} -> DescID: {did}")
            except:
                pass

if __name__ == '__main__':
    main()