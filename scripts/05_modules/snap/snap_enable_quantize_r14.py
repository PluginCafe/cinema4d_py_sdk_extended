"""
Copyright: MAXON Computer GmbH

Description:
    - Enables the quantize if it's not already the case.
    - Defines quantize Move and Scale step.

Class/method highlighted:
    - c4d.modules.snap
    - c4d.modules.snap.GetSnapSettings()
    - c4d.modules.snap.SetSnapSettings()
    - c4d.modules.snap.IsQuantizeEnabled()
    - c4d.modules.snap.SetQuantizeStep()
    - c4d.modules.snap.GetQuantizeStep()

Compatible:
    - Win / Mac
    - R14, R15, R16, R17, R18, R19, R20, R21
"""
import c4d


def main():
    # Enables quantizing
    settings = c4d.modules.snap.GetSnapSettings(doc)
    settings[c4d.QUANTIZE_ENABLED] = True
    c4d.modules.snap.SetSnapSettings(doc, settings)
    print "Quantize Enabled:", c4d.modules.snap.IsQuantizeEnabled(doc)

    # Sets quantize scale step
    c4d.modules.snap.SetQuantizeStep(doc, None, c4d.QUANTIZE_SCALE, 0.5)
    print "Quantize Scaling Step:", c4d.modules.snap.GetQuantizeStep(doc, None, c4d.QUANTIZE_SCALE)

    # Sets quantize move step
    c4d.modules.snap.SetQuantizeStep(doc, None, c4d.QUANTIZE_MOVE, 25)
    print "Quantize Movement Step:", c4d.modules.snap.GetQuantizeStep(doc, None, c4d.QUANTIZE_MOVE)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()