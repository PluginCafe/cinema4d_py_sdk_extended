"""
Copyright: MAXON Computer GmbH

Description:
    - Retrieves all selected clones of the active Cloner object.

Class/method highlighted:
    - c4d.modules.mograph.GeGetMoDataSelection()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Checks if there is an active object
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Checks if the active object is a MoGraph Cloner Object
    if not op.CheckType(1018544):
        raise TypeError("Selected object is not a Mograph Cloner Object.")

    # Retrieves MoGraph Selection Tag from the cloner
    tag = op.GetTag(c4d.Tmgselection)
    if tag is None:
        raise RuntimeError("Failed to retrieve a MoGraph Selection Tag on the selected object.")

    # Retrieves the clones selection
    selection = c4d.modules.mograph.GeGetMoDataSelection(tag)

    # Retrieves selection list
    count = op[c4d.MG_LINEAR_COUNT]

    # Retrieves selected clones indices
    indices = []
    for index in range(count):
        if selection.IsSelected(index):
            indices.append(index)

    print("Clones selection indices:", indices)


if __name__ == '__main__':
    main()
