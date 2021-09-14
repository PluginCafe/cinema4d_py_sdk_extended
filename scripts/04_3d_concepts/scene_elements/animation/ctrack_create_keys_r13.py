"""
Copyright: MAXON Computer GmbH
Author: Manuel MAGALHAES

Description:
    - Creates position Y tracks.
    - Adds two keyframes.
    - Sets their value and interpolation.

Class/method highlighted:
    - CKey.SetInterpolation()
    - CKey.SetKeyDefault()

"""

import c4d


def CreateKey(curve, time, value, interpolation):
    """Creates a Key on the given curve at the given time with a given value and with the given interpolation.

    Args:
        curve (c4d.CCurve): The Curve where to add the keyframe.
        time (c4d.BaseTime): The time of the keyframe.
        value (float): The value of the keyframe.
        interpolation (c4d.CINTERPOLATION_XXX): The interpolation of the key along the curve.

    Returns:
        tuple(c4d.Ckey, int)

    Raises:
        MemoryError: If for some reason, it was not possible to create the key.
    
    Returns:
        c4d.CKey, int: They key and the index of the key in the CCurve.
    """
    # Adds the key
    keyDict = curve.AddKey(time)

    # Checks if the key have been added
    if keyDict is None:
        raise MemoryError("Failed to create a key")

    # Retrieves the inserted key
    key = keyDict["key"]
    keyIndex = keyDict["nidx"]

    # Sets the value of the key
    key.SetValue(curve, value)

    # Mandatory: Fill the key with default settings
    curve.SetKeyDefault(doc, keyIndex)

    # Changes it's interpolation
    key.SetInterpolation(curve, interpolation)

    return key, keyIndex


def main():
    # Creates the object in memory
    obj = c4d.BaseObject(c4d.Ocube)

    # Creates the track in memory. Defined by it's DescID
    trackY = c4d.CTrack(obj, c4d.DescID(c4d.DescLevel(c4d.ID_BASEOBJECT_REL_POSITION, c4d.DTYPE_VECTOR, 0),
                                        c4d.DescLevel(c4d.VECTOR_Y, c4d.DTYPE_REAL, 0)))

    # Gets curves for the track
    curveY = trackY.GetCurve()

    # Creates a key in the Y curve with value 0 at 0 frame with a spline interpolation
    keyA, keyAIndex = CreateKey(curveY, c4d.BaseTime(0), value=0, interpolation=c4d.CINTERPOLATION_SPLINE)

    # Retrieves time at frame 10
    keyBTime = c4d.BaseTime(10, doc.GetFps())

    # Creates another key in the Y curve with value 100 at 10 frame with a spline interpolation
    keyB, keyBIndex = CreateKey(curveY, keyBTime, value=100, interpolation=c4d.CINTERPOLATION_SPLINE)

    # Inserts the track containing the Y curve to the object
    obj.InsertTrackSorted(trackY)

    # Inserts the object in document
    doc.InsertObject(obj)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


# Execute main()
if __name__ == '__main__':
    main()
