"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Imports STP/STEP with custom settings.

Class/method highlighted:
    - c4d.plugins.FindPlugin()
    - MSG_RETRIEVEPRIVATEDATA
    - c4d.documents.MergeDocument()

Documentation links:
    - https://developers.maxon.net/docs/Cinema4DPythonSDK/html/consts/FORMAT_export.html
    - https://developers.maxon.net/docs/Cinema4DCPPSDK/html/_fcadimport_8h.html

"""
import c4d


def main():
    # Retrieves a path to load the imported file
    selectedFile = c4d.storage.LoadDialog(title="Load File for STEP Import", type=c4d.FILESELECTTYPE_ANYTHING, force_suffix="step")
    if not selectedFile:
        return

    # Retrieves STEP import plugin
    plug = c4d.plugins.FindPlugin(c4d.FORMAT_STEPIMPORT, c4d.PLUGINTYPE_SCENELOADER)
    if plug is None:
        raise RuntimeError("Failed to retrieve the STEP importer.")

    data = dict()
    # Sends MSG_RETRIEVEPRIVATEDATA to STEP import plugin
    if not plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, data):
        raise RuntimeError("Failed to retrieve private data.")

    # BaseList2D object stored in "imexporter" key hold the settings
    stepImport = data.get("imexporter", None)
    if stepImport is None:
        raise RuntimeError("Failed to retrieve BaseContainer private data.")

    # Defines the settings
    stepImport[c4d.CADIMPORT_SPLINES] = False

    stepImport[c4d.CADIMPORT_ORIGINAL_UNITS] = False
    # Sets the data by Scaling 10x and set to mm units
    scale = c4d.UnitScaleData()
    scale.SetUnitScale(10, c4d.DOCUMENT_UNIT_MM)
    stepImport[c4d.CADIMPORT_SCALE] = scale

    # Finally imports without dialogs
    if not c4d.documents.MergeDocument(doc, selectedFile, c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS, None):
        raise RuntimeError("Failed to load the document.")

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
