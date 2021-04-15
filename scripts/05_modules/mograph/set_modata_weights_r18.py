"""
Copyright: MAXON Computer GmbH

Description:
    - Sets a weight of 1.0 for all clones of the active Cloner object.

Class/method highlighted:
    - c4d.modules.mograph.GeSetMoDataWeights()

"""
import c4d


def main():
    # Checks if there is an active object
    if op is None:
        raise ValueError("op is None, please select one object.")

    # Checks if the active object is a MoGraph Cloner Object
    if not op.CheckType(1018544):
        raise TypeError("Selected object is not a Mograph Cloner Object.")

    # Builds list for clones weights values
    weights = [1.0] * op[c4d.MG_LINEAR_COUNT]

    # Sets clones weights values
    c4d.modules.mograph.GeSetMoDataWeights(op, weights)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
