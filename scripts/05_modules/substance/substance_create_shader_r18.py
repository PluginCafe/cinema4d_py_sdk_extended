"""
Copyright: MAXON Computer GmbH
Author: Andreas Block

Description:
    - Creates a new substance shader linked to the given substance asset.
    - The asset is scanned for a bump output channel that is used in that shader.

Class/method highlighted:
    - c4d.modules.substance.GetFirstSubstance()
    - c4d.modules.substance.GetSubstanceGraph()
    - c4d.modules.substance.CreateSubstanceShader()
    - c4d.modules.substance.GetSubstanceOutput()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Retrieves active material
    mat = doc.GetActiveMaterial()
    if mat is None:
        raise RuntimeError("Failed to retrieve the selected material.")

    # Checks if the selected material is a standard material
    if not mat.IsInstanceOf(c4d.Mmaterial):
        raise TypeError("mat is not a c4d.Mmaterial.")

    # Retrieves first substance
    substance = c4d.modules.substance.GetFirstSubstance(doc)
    if substance is None:
        raise RuntimeError("Failed to retrieve the first substance (most likely there is no substance).")

    # Retrieves substance graph
    graph, graphName = c4d.modules.substance.GetSubstanceGraph(substance)
    if graph is None:
        raise RuntimeError("Failed to retrieve substance graph.")

    # Creates a new substance shader
    shader = c4d.modules.substance.CreateSubstanceShader(substance)
    if shader is None:
        raise MemoryError("Failed to create a substance shader.")

    # Inserts shader into material and use it in bump channel
    mat.InsertShader(shader)
    mat[c4d.MATERIAL_BUMP_SHADER] = shader
    mat[c4d.MATERIAL_USE_BUMP] = True

    # Loops trough all output channels
    output, outputUid, outputType, outputName, outputBmp = c4d.modules.substance.GetSubstanceOutput(substance, graph, True)
    while output is not None:
        # Checks if outputType is a bump output channel
        if outputType == c4d.SUBSTANCE_OUTPUT_TYPE_BUMP:
            shader.SetParameter(c4d.SUBSTANCESHADER_CHANNEL, outputUid, c4d.DESCFLAGS_SET_0)

        # Retrieves data from the Substance Output
        output, outputUid, outputType, outputName, outputBmp = c4d.modules.substance.GetSubstanceOutput(substance, graph, True, output)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
