"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Reads the vector components curves of the active object's rotation track curve.

Class/method highlighted:
    - BaseObject.FindBestEulerAngle()
    - BaseObject.GetVectorCurves()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21
"""
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

    # Gets the curve for the track
    curve = track.GetCurve()
    if curve is None:
        raise RuntimeError("Failed to retrieve the curves, Object may not have curves.")

    # Gets the X,Y,Z curves from a Vector curve
    ret, curveX, curveY, curveZ = op.GetVectorCurves(curve)
    if not ret:
        raise RuntimeError("Failed to retrieve the vector curve.")

    print "c4d.ID_BASEOBJECT_REL_ROTATION curves:"
    print "Curve H:", curveX
    print "Curve P:", curveY
    print "Curve B:", curveZ


if __name__ == '__main__':
    main()