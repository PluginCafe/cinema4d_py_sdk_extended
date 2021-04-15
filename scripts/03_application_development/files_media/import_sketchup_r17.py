"""
Copyright: MAXON Computer GmbH
Author: Joey Gaspe

Description:
    - Imports Sketchup File with custom settings.

Class/method highlighted:
    - c4d.plugins.FindPlugin()
    - MSG_RETRIEVEPRIVATEDATA
    - c4d.documents.MergeDocument()

"""
import c4d


def main():
    # Retrieves a path to load the imported file
    selectedFile = c4d.storage.LoadDialog(title="Load File for SketchUp Import", type=c4d.FILESELECTTYPE_ANYTHING, force_suffix="skp")
    if not selectedFile:
        return

    # Retrieves SketchUp import plugin, 1033845 is its ID
    plug = c4d.plugins.FindPlugin(c4d.FORMAT_SKPIMPORT, c4d.PLUGINTYPE_SCENELOADER)
    if plug is None:
        raise RuntimeError("Failed to retrieve the SketchUp importer.")

    data = dict()
    # Sends MSG_RETRIEVEPRIVATEDATA to SketchUp import plugin
    if not plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, data):
        raise RuntimeError("Failed to retrieve private data.")

    # BaseList2D object stored in "imexporter" key hold the settings
    skpImport = data.get("imexporter", None)
    if skpImport is None:
        raise RuntimeError("Failed to retrieve BaseContainer private data.")

    # Defines the settings
    skpImport[c4d.SKPIMPORT_DAYLIGHT_SYSTEM_PHYSICAL_SKY] = True
    skpImport[c4d.SKPIMPORT_CAMERA] = True
    skpImport[c4d.SKPIMPORT_SKIP_HIDDEN_OBJECTS] = True
    skpImport[c4d.SKPIMPORT_SPLIT_OBJECTS_BY_LAYER] = True
    skpImport[c4d.SKPIMPORT_SHOW_STATISTICS_IN_CONSOLE] = True

    # Finally imports without dialogs
    if not c4d.documents.MergeDocument(doc, selectedFile, c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS, None):
        raise RuntimeError("Failed to load the document.")

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
