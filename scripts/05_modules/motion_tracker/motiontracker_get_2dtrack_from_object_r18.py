"""
Copyright: MAXON Computer GmbH

Description:
    -  Loops through all the tracks of the active Motion Tracker object.

Class/method highlighted:
    - BaseObject.Get2dTrackData()
    - Mt2dTrackData.GetTrackCount()
    - Mt2dTrackData.GetTrackByIndex()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21
"""
import c4d


def main():
    # Checks if there is an active object
    if op is None:
        raise ValueError("op is None, please select one object.")

    # Checks if the selected object is a Motion Tracker Object
    if not op.IsInstanceOf(c4d.Omotiontracker):
        raise TypeError("op is not a c4d.Omotiontracker.")

    # Retrieves tracking data
    data = op.Get2dTrackData()
    if data is None:
        raise RuntimeError("Failed to retrieve the 2D track data.")

    # Loops through all tracks
    trackCount = data.GetTrackCount()
    for trackIdx in xrange(trackCount):
        track = data.GetTrackByIndex(trackIdx)
        if track is None:
            continue

        # Checks track status
        status = track.GetStatus()
        statusStr = ""
        if status == c4d.INVALID_TRACK:
            statusStr = "invalid"
        elif status == c4d.UNTRACKED:
            statusStr = "untracked"
        elif status == c4d.TRACKED_VALID:
            statusStr = "valid"
        elif status == c4d.TRACKED_STALE:
            statusStr = "stale"

        # Prints track information
        print "Track #{0}: {1} is {2}".format(trackIdx, track.GetName(), statusStr)


if __name__ == '__main__':
    main()