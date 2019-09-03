"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Configures OpenEXR output render format with SetImageSettingsDictionary() then reads these with GetImageSettingsDictionary().

Class/method highlighted:
    - c4d.bitmaps.SetImageSettingsDictionary()
    - c4d.bitmaps.GetImageSettingsDictionary()

Compatible:
    - Win / Mac
    - R20, R21
"""
import c4d
import maxon


def main():
    # Retrieves render data and its container
    renderData = doc.GetActiveRenderData()
    bc = renderData.GetDataInstance()

    # Gets image filters options
    saveOptions = bc.GetContainerInstance(c4d.RDATA_SAVEOPTIONS)

    # Sets OpenEXR output format
    bc[c4d.RDATA_FORMAT] = c4d.FILTER_EXR

    # Defines OpenEXR settings
    compressionmethodID = maxon.Id('net.maxon.mediasession.openexr.export.compressionmethod')
    halffloatID = maxon.Id('net.maxon.mediasession.openexr.export.halffloat')
    layernumberingID = maxon.Id('net.maxon.mediasession.openexr.export.layernumbering')

    # Configures OpenEXR format options with a maxon.DataDictionary
    exportSettings = maxon.DataDictionary()
    exportSettings.Set(compressionmethodID, maxon.Id("rle"))
    exportSettings.Set(halffloatID, True)
    exportSettings.Set(layernumberingID, True)

    # Stores settings in render data container
    c4d.bitmaps.SetImageSettingsDictionary(exportSettings, saveOptions, c4d.FILTER_EXR)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()

    # Retrieves OpenEXR images settings
    settings = c4d.bitmaps.GetImageSettingsDictionary(saveOptions, c4d.FILTER_EXR)

    # Reads and prints OpenEXR format options
    print("openexr.export.compressionmethod: " + str(settings.Get(compressionmethodID)))
    print("openexr.export.halffloat: " + str(settings.Get(halffloatID)))
    print("openexr.export.layernumbering: " + str(settings.Get(layernumberingID)))


if __name__ == '__main__':
    main()