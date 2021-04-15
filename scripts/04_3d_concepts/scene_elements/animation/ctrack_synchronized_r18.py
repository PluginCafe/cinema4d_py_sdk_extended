"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Checks if the rotation track of an object is synchronized. If not, it will be synchronized.

Class/method highlighted:
    - CTrack.IsSynchronized()
    - CTrack.SetSynchronized()

"""
# This example checks if the rotation track of an object is synchronized. If not, it will be synchronized.
import c4d

def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Searches object's rotation track
    trackID = c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_REL_ROTATION, c4d.DTYPE_VECTOR, op.GetType()))
    track = op.FindCTrack(trackID)
    if track is None:
        raise RuntimeError("Failed to retrieve the track, Object may not have track.")

    # Check if the track is not synchronized
    if not track.IsSynchronized():
        # If not synchronize its components tracks
        track.SetSynchronized(True);

        # Pushes an update event to Cinema 4D
        c4d.EventAdd()
        print('Synchronized Object "{0}" Track "{1}"'.format(op.GetName(), track.GetName()))


if __name__ == '__main__':
    main()
