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
"""
import c4d
import maxon


def main():
    # Retrieve the selected baseMaterial
    mat = doc.GetActiveMaterial()
    if mat is None:
        raise ValueError("There is no selected BaseMaterial")

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

    def ToogleMuteSelectedWires(sourcePort, destinationPort, wire):
        """
        Toggle INHIBIT flag wires responsible to define if a wire is muted or not.
        This function is used as a callback parameter of NodesGraphModelInterface.GetSelectedWires.

        Args:
            sourcePort: (maxon.GraphNode): The input port of the wire.
            destinationPort: (maxon.GraphNode): The output port of the wire.
            wire: (maxon.Wires): The wire flag defining the behavior of the connection from the input to the output port.

        Returns:
            bool: **True** will continue to call ToogleMuteSelectedWires on next connection, otherwise **False**
        """
        if wire[maxon.Wires.INHIBIT] == maxon.WIRE_MODE.NORMAL:
            # Unmute the wire.
            wire[maxon.Wires.INHIBIT] = maxon.WIRE_MODE.REMOVE
        else:
            # Mute the wire.
            wire[maxon.Wires.INHIBIT] = maxon.WIRE_MODE.NORMAL
        sourcePort.Connect(destinationPort, modes=wire)
        return True

    # To modify a graph, modification must be done inside a transaction.
    # After modifications are done, the transaction must be committed.
    with graph.BeginTransaction() as transaction:
        maxon.GraphModelHelper.GetSelectedConnections(graph, ToogleMuteSelectedWires)
        transaction.Commit()

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
