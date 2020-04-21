"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Loops through all override groups and checks which groups are currently selected.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.GetCurrentTake()
    - BaseTake.GetOverrideGroups()

Compatible:
    - Win / Mac
    - R17, R18, R19, R20, R21, S22
"""
import c4d


def main():
    # Gets the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Gets the active Take
    take = takeData.GetCurrentTake()
    if take is None:
        raise RuntimeError("Failed to retrieve the current take.")

    # Retrieves all overrides groups for this Take
    overrideGroups = take.GetOverrideGroups()

    # Loops over all groups
    for group in overrideGroups:

        # Print the group name and its selection state
        print("Group {0}, isSelected: {1}".format(group.GetName(), bool(group.GetBit(c4d.BIT_ACTIVE))))


if __name__ == '__main__':
    main()
