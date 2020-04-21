"""
Copyright: MAXON Computer GmbH

Description:
    - Enables the snap if it's not already the case.
    - Sets it to 3D Type and also to Point mode.

Class/method highlighted:
    - c4d.modules.snap
    - c4d.modules.snap.IsSnapEnabled()
    - c4d.modules.snap.GetSnapSettings()
    - c4d.modules.snap.SetSnapSettings()
    - c4d.modules.snap.EnableSnap()

Compatible:
    - Win / Mac
    - R14, R15, R16, R17, R18, R19, R20, R21, S22
"""
import c4d


def main():
    # Checks snap state
    res = c4d.modules.snap.IsSnapEnabled(doc)
    if not res:
        # Enables snap if not activated
        c4d.modules.snap.EnableSnap(True, doc)
        print("Snap Enabled:", c4d.modules.snap.IsSnapEnabled(doc))

    # Retrieves the BaseContainer storing all the settings
    settings = c4d.modules.snap.GetSnapSettings(doc)

    # Defines the snapping Type to 3D snapping
    settings[c4d.SNAP_SETTINGS_MODE] = c4d.SNAP_SETTINGS_MODE_3D

    # Pushes back modification made in the memory BaseContainer to the BaseContainer setting
    c4d.modules.snap.SetSnapSettings(doc, settings)

    # Enables point snap
    c4d.modules.snap.EnableSnap(True, doc, c4d.SNAPMODE_POINT)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
