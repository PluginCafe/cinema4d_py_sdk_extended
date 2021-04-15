"""
Copyright: MAXON Computer GmbH
Author: Sebastian Bach

Description:
    - Loops through the child Takes of the main Take
    - Save the state of each child Take to a document.

Class/method highlighted:
    - BaseDocument.GetTakeData()
    - TakeData.GetMainTake()
    - TakeData.TakeToDocument()
    - GeListNode.GetDown()
    - GeListNode.GetNext()

"""
import c4d
import os


def main():
    # Gets the TakeData from the active document (holds all information about Takes)
    takeData = doc.GetTakeData()
    if takeData is None:
        raise RuntimeError("Failed to retrieve the take data.")

    # Gets the main Take, aka the first one
    mainTake = takeData.GetMainTake()
    if mainTake is None:
        raise RuntimeError("Failed to retrieve the main take.")

    # Get the child of this one
    childTake = mainTake.GetDown()
    if childTake is None:
        raise RuntimeError("There is no children of this take.")

    # Open a dialog to selected a folder where all files will be saved
    folder = c4d.storage.LoadDialog(c4d.FILESELECTTYPE_ANYTHING, "Select Folder", c4d.FILESELECT_DIRECTORY)
    if not folder:
        return

    # Loops over all Takes
    while childTake:

        # Convert a Take to a BaseDocument
        takeDoc = takeData.TakeToDocument(childTake)
        if takeDoc is not None:

            # Generates the full path to save the file
            fileName = childTake.GetName() + ".c4d"
            fullFileName = os.path.join(folder, fileName)

            # Saves the documents
            c4d.documents.SaveDocument(takeDoc, fullFileName, saveflags=c4d.SAVEDOCUMENTFLAGS_0,format=c4d.FORMAT_C4DEXPORT)

        # Next loop, childTake, will be equal to the next Take.
        # At the end it will be None, and the loop will leave
        childTake = childTake.GetNext()


if __name__ == '__main__':
    main()
