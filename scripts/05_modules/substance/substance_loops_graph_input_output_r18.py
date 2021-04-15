"""
Copyright: MAXON Computer GmbH
Author: Andreas Block

Description:
    - Loops through the graphs of the given substance asset.
    - Loops through the inputs and outputs of each graph.

Class/method highlighted:
    - c4d.modules.substance.GetFirstSubstance()
    - c4d.modules.substance.GetSubstanceGraph()
    - c4d.modules.substance.GetSubstanceInput()
    - c4d.modules.substance.GetSubstanceOutput()

"""
import c4d


def main():
    # Retrieves first substance
    substance = c4d.modules.substance.GetFirstSubstance(doc)
    if substance is None:
        raise RuntimeError("Failed to retrieve the first substance (most likely there is no substance).")

    # Loops through graphs
    graph, graphName = c4d.modules.substance.GetSubstanceGraph(substance)
    while graph is not None:
        print("Graph Name: " + graphName)

        # Loops through inputs
        substanceInput, inputUid, firstId, numElements, inputType, inputName = c4d.modules.substance.GetSubstanceInput(substance, graph)
        while substanceInput is not None:
            print("Input: " + inputName)
            substanceInput, inputUid, firstId, numElements, inputType, inputName = c4d.modules.substance.GetSubstanceInput(substance, graph, substanceInput)

        # Loops through outputs
        output, outputUid, outputType, outputName, outputBmp = c4d.modules.substance.GetSubstanceOutput(substance, graph, True)
        while output is not None:
            print("Output: " + outputName)
            output, outputUid, outputType, outputName, outputBmp = c4d.modules.substance.GetSubstanceOutput(substance, graph, True, output)

        graph, graphName = c4d.modules.substance.GetSubstanceGraph(substance, graph)


if __name__ == '__main__':
    main()
