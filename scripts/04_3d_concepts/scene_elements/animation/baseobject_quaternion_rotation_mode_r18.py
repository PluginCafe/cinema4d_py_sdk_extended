"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Checks if the active object uses quaternion interpolation.

Class/method highlighted:
    - BaseObject.IsQuaternionRotationMode()
    - BaseObject.SetQuaternionRotationMode()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Checks if selected object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Check if the object uses quaternion interpolation
    if not op.IsQuaternionRotationMode():
        # Enable quaternion interpolation
        # This will update the object's rotation animation tracks
        op.SetQuaternionRotationMode(True, False)
        c4d. EventAdd()


if __name__ == '__main__':
    main()
