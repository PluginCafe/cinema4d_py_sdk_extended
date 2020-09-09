"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Retrieves a complete DescID (with datatype and creator IDs) from another DescID.

Class/method highlighted:
    - Description.CheckDescID()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")
    
    # Retrieves the active object's description
    desc = op.GetDescription(c4d.DESCFLAGS_DESC_0)
    if desc is None:
        raise RuntimeError("Failed to retrieve the description.")

    # Builds the object's X position parameter DescID
    descId = c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_POSITION, 0, 0), c4d.DescLevel(c4d.VECTOR_X, 0, 0))

    # Prints previously built DescID
    print(descId)

    # Calls CheckDescID() to retrieve the complete DescID for the object's X position parameter
    ret = desc.CheckDescID(descId, [op])
    if ret is None:
        raise RuntimeError("Could not check description ID.")

    # Prints the complete DescID
    print(ret)


if __name__ == '__main__':
    main()
