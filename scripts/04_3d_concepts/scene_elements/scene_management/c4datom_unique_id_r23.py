"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Adds a unique ID to the active Object.
    - Iterate all uniques IDs of the active Object.
    - Find a particular unique ID from the active object.

Class/method highlighted:
    - C4DAtom.AddUniqueID()
    - C4DAtom.GetUniqueIDCount()
    - C4DAtom.GetUniqueIDIndex()
    - C4DAtom.FindUniqueID()

Compatible:
    - Win / Mac
    - R23
"""
import c4d


def main():
    # Obtained from www.plugincafe.com
    uniqueID = 100000

    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Adds a data to the Unique ID elements
    op.AddUniqueID(uniqueID, b"test")

    # Iterate over all unique IDs elements
    for x in range(op.GetUniqueIDCount()):
        uId, byt = op.GetUniqueIDIndex(x)
        print(uId, byt)

    # FindUniqueID can be used to retrieve a specific Unique ID, in this case retrieve the internal GeMarker of an object.
    # On object creation, a new GeMarker is generated based on some document related data.
    # Each marker is unique to each document, this can be used to identify a similar object over time.
    memoryView = op.FindUniqueID(c4d.MAXON_CREATOR_ID)
    print(memoryView.tobytes())


# Execute main()
if __name__=='__main__':
    main()
