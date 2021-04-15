"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Checks the interpolation of the first key for an object's rotation track.
    - If the interpolation is linear (SLERP) it is changed to cubic.

Note:
    - The object has to be in quaternion rotation mode.

Class/method highlighted:
    - BaseObject.IsQuaternionRotationMode()
    - BaseObject.GetQuatInterpolation()
    - BaseObject.SetQuatInterpolation()

"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Only continue if object is in quaternion rotation mode
    if not op.IsQuaternionRotationMode():
        raise RuntimeError("Object mode is not set to quaternion mode.")

    # Searches object's rotation track
    trackID = c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_REL_ROTATION, c4d.DTYPE_VECTOR, op.GetType()))
    track = op.FindCTrack(trackID)
    if track is None:
        raise RuntimeError("Failed to retrieve the track, Object may not have track.")

    # Retrieves the curve for the track
    curve = track.GetCurve()
    if curve is None:
        raise RuntimeError("Failed to retrieve the curves, Object may not have curves.")

    # Does not continue if there are no keys inside curve
    if curve.GetKeyCount() == 0:
        raise RuntimeError("There is no keys on the curve.")

    # Retrieves first key
    key = curve.GetKey(0)
    if key is None:
        raise RuntimeError("Failed to retrieve they first key of the curve.")

    # Checks quaternion interpolation is linear (SLERP)
    if key.GetQuatInterpolation() == c4d.ROTATIONINTERPOLATION_QUATERNION_SLERP:
        # If yes, change it to cubic
        key.SetQuatInterpolation(curve, c4d.ROTATIONINTERPOLATION_QUATERNION_CUBIC)

        # Pushes an update event to Cinema 4D
        c4d.EventAdd()


if __name__ == '__main__':
    main()
