"""
Copyright: MAXON Computer GmbH

Description:
    - Retrieves the weights from all clones of the active Cloner object.

Class/method highlighted:
    - c4d.modules.mograph.GeGetMoDataWeights()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21
"""
import c4d


def main():
    # Checks if there is an active object
    if op is None:
        raise ValueError("op is None, please select one object.")

    # Checks if the active object is a MoGraph Cloner Object
    if not op.CheckType(1018544):
        raise TypeError("Selected object is not a Mograph Cloner Object.")

    # Retrieves MoGraph Weight Tag from the cloner
    tag = op.GetTag(c4d.Tmgweight)
    if tag is None:
        raise RuntimeError("Failed to retrieve a Mograph Weight Tag on the selected object.")

    # Retrieves the clones weight values
    weights = c4d.modules.mograph.GeGetMoDataWeights(tag)

    # Prints clones weights
    print "'" + op.GetName() + "'", "Clones Weights:"

    for index, value in enumerate(weights):
        print index, ":", value


if __name__ == '__main__':
    main()