"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Loops over all documents opened in Cinema 4D.

Notes:
    All documents are passed through even the one not listed in the Windows menu.

Class/method highlighted:
    - c4d.documents.GetFirstDocument()
    - c4d.documents.GetDocumentName()
    - BaseList2D.GetNext()

"""
import c4d


def main():
    # Retrieves the first documents
    doc = c4d.documents.GetFirstDocument()
    if doc is None:
        raise RuntimeError("No document found, this is very unexpected but can happen in commandline.")

    # Loops until doc is None
    while doc is not None:

        # Prints the name of the document
        print(doc.GetDocumentName())

        # Assigns doc variable to the next document
        doc = doc.GetNext()


if __name__ == "__main__":
    main()
