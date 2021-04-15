"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Iterates over all markers of the active document.
    - Prints all markers of the Frame 30.

Class/method highlighted:
    - c4d.documents.GetFirstMarker()
    - BaseList2D.GetNext()

"""
import c4d


def main():
    markerAtFrame30 = list()

    # Retrieves the first Marker
    marker = c4d.documents.GetFirstMarker(doc)

    # Loops until marker is undefined
    while marker is not None:

        # Retrieves the time of the marker in fps
        markerTime = marker[c4d.TLMARKER_TIME]
        markerFrame = markerTime.GetFrame(doc.GetFps())

        # Retrieves the time of the length in fps
        lengthTime = marker[c4d.TLMARKER_LENGTH]
        lengthFrame = lengthTime.GetFrame(doc.GetFps())

        # if frame 30 is between the marker frame and the marker length, add to the final list
        if markerFrame <= 30 <= markerFrame + lengthFrame:
            markerAtFrame30.append(marker)

        # Since a marker is a BaseList2D we can use GetNext for iterate
        marker = marker.GetNext()

    print(markerAtFrame30)


if __name__ == "__main__":
    main()
