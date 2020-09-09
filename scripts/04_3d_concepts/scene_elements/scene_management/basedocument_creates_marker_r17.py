"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates 2 markers.

Class/method highlighted:
    - c4d.documents.GetFirstDocument()
    - c4d.documents.GetDocumentName()
    - BaseList2D.GetNext()

Compatible:
    - Win / Mac
    - R17, R18, R19, R20, R21, S22, R23
"""
import c4d

def main():
    # Retrieves the FPS of the document
    fps = doc.GetFps()

    # Creates a first marker
    firstMarker = c4d.documents.AddMarker(doc, None, c4d.BaseTime(30, fps), "First Marker")

    # Creates a second marker with a duration of 5 frame
    secondMarker = c4d.documents.AddMarker(doc, None, c4d.BaseTime(27, fps), "Second Marker")
    secondMarker[c4d.TLMARKER_LENGTH] = c4d.BaseTime(5, fps)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
