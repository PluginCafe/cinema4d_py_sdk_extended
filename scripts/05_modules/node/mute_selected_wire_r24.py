"""
Copyright: MAXON Computer GmbH
Author: Manuel Magalhaes

Description:
    Retrieve the selected node material and toggle-mute the selected 
    connection, i.e., if the connection is muted, it will be unmuted or 
    vice-versa. A connection is composed out of eight wires, to mute the 
    connection, one must set the INHIBIT wire to WIRE_MODE.NORMAL. To unmute 
    the connection, one must set the INHIBIT wire to WIRE_MODE.REMOVE.
    
Class/method highlighted:
    - GetSelectedWires
    - IsSelected
    - 
"""
import c4d
import maxon
import maxon.frameworks.nodespace
import maxon.frameworks.nodes


def main():
    # Retrieve the selected baseMaterial
    mat = doc.GetActiveMaterial()
    if mat is None:
        raise ValueError("Cannot create a BaseMaterial")

    # Retrieve the reference of the material as a node Material.
    nodeMaterial = mat.GetNodeMaterialReference()
    if nodeMaterial is None:
        raise ValueError("Cannot retrieve NodeMaterial reference")

    # Retrieve the current node space Id
    nodespaceId = c4d.GetActiveNodeSpaceId()

    # Retrieve the Nimbus reference for a specific nodeSpace
    nimbusRef = mat.GetNimbusRef(nodespaceId)
    if nimbusRef is None:
        raise ValueError("Cannot retrieve the nimbus ref for that node space")

    # Retrieve the graph corresponding to that nodeSpace.
    graph = nimbusRef.GetGraph()
    if graph is None:
        raise ValueError("Cannot retrieve the graph of this nimbus reference")

    # Get the root of the GraphNode
    root = graph.GetRoot()

    # Retrieve all the wires
    selectedWires = list()

    def ToogleMuteSelectedWires(sourcePort, destinationPort, wire):
        if (wire[maxon.frameworks.graph.Wires.INHIBIT] ==
                maxon.frameworks.graph.WIRE_MODE.NORMAL):
            # Unmute the wire.
            remove = maxon.frameworks.graph.WIRE_MODE.REMOVE
            wire[maxon.frameworks.graph.Wires.INHIBIT] = remove
        else:
            # Mute the wire.
            normal = maxon.frameworks.graph.WIRE_MODE.NORMAL
            wire[maxon.frameworks.graph.Wires.INHIBIT] = normal
        sourcePort.Connect(destinationPort, modes=wire)
        return True

    # To modify a graph, modification must be done inside a transaction.
    # After modifications are done, the transaction must be committed.
    with graph.BeginTransaction() as transaction:
        graph.GetSelectedWires(ToogleMuteSelectedWires)
        transaction.Commit()

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
