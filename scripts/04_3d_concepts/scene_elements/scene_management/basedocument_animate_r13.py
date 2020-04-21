"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Animates a BaseDocument from frame 5 to 20.
    - Updates the Progress Bar of Cinema 4D.

Class/method highlighted:
    - c4d.StatusSetBar()
    - c4d.StatusClear()
    - c4d.BaseTime()
    - BaseDocument.SetTime()
    - c4d.GeSyncMessage()
    - c4d.DrawViews()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22
"""
import c4d


def main():
    # Saves current time
    ctime = doc.GetTime()

    # Retrieves BaseTime of frame 5, 20
    start = 5
    end = 20

    # Loops through the frames
    for frame in range(start, end + 1):

        # Sets the Status Bar
        c4d.StatusSetBar(100.0 * float(frame - start) / float(end - start))

        # Changes the time of the document
        doc.SetTime(c4d.BaseTime(frame, doc.GetFps()))

        # Updates timeline
        c4d.GeSyncMessage(c4d.EVMSG_TIMECHANGED)

        # Redraws the viewport and regenerate the cache object
        c4d.DrawViews(c4d.DRAWFLAGS_ONLY_ACTIVE_VIEW | c4d.DRAWFLAGS_NO_THREAD | c4d.DRAWFLAGS_NO_REDUCTION | c4d.DRAWFLAGS_STATICBREAK)

        # Do the stuff for each frame here you may be interested in BaseDocument.Polygonize()
        print("Frame {0}".format(frame))

    # Sets the time back to the original time.
    doc.SetTime(ctime)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd(c4d.EVENT_ANIMATE)

    # Clears the Status Bar
    c4d.StatusClear()


if __name__ == "__main__":
    main()
