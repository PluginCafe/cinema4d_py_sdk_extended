# Xpresso

XPRESSO is the old node-based system to create custom expressions. This is not the nodal system for Cinema 4D Node Material. 

Classic API:
- **c4d.XpressoTag**: *Stores a node system and returns the GvNodeMaster.*
- **c4d.modules.graphview.GvNodeMaster**: *Stores a collection of GvNode, gives access to the stored nodes and is used to create new nodes.*
- **c4d.modules.graphview.GvNode**: *Represents a single node.*
- **c4d.modules.graphview.GvPort**: *Represents a single port of a node. Connection between GvNode, are done through GvPort.*

## Examples

### gvnode_delete
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21 - Win/Mac

    Deletes the first node created from the Xpresso Tag of the selected object.

### gvnode_move
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21 - Win/Mac

    Moves the first node in the Graph View created from the Xpresso Tag of the selected object.

### gvnodemaster_creates_connects_nodes
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21 - Win/Mac

    Creates a Constants and Results node in the Xpresso Tag of the selected object.
    Connects both Nodes together.

### gvnodemaster_from_xpresso_tag
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21 - Win/Mac

    Retrieves the Node Master (The BaseList2D object that holds all nodes) from an Xpresso Tag.

### gvnodemaster_loops_nodes
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21 - Win/Mac

    Loops through all nodes from the Xpresso Tag of the selected object.
    Checks if it's a Constant Node.
