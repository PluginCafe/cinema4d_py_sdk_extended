"""
Copyright: MAXON Computer GmbH
Author: Joey Gaspe

Description:
    - Imports Obj with custom settings.

Class/method highlighted:
    - c4d.plugins.FindPlugin()
    - MSG_RETRIEVEPRIVATEDATA
    - c4d.documents.MergeDocument()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Retrieves a path to load the imported file
    selectedFile = c4d.storage.LoadDialog(title="Load File for OBJ Import", type=c4d.FILESELECTTYPE_ANYTHING, force_suffix="obj")
    if not selectedFile:
        return

    # Retrieves Obj import plugin, defined in R17 as FORMAT_OBJ2IMPORT and below R17 as FORMAT_OBJIMPORT
    objExportId = c4d.FORMAT_OBJIMPORT if c4d.GetC4DVersion() < 17000 else c4d.FORMAT_OBJ2IMPORT
    plug = c4d.plugins.FindPlugin(objExportId, c4d.PLUGINTYPE_SCENELOADER)
    if plug is None:
        raise RuntimeError("Failed to retrieve the obj importer.")

    data = dict()
    # Sends MSG_RETRIEVEPRIVATEDATA to OBJ import plugin
    if not plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, data):
        raise RuntimeError("Failed to retrieve private data.")

    # BaseList2D object stored in "imexporter" key hold the settings
    objImport = data.get("imexporter", None)
    if objImport is None:
        raise RuntimeError("Failed to retrieve BaseContainer private data.")

    # Defines the settings
    objImport[c4d.OBJIMPORTOPTIONS_PHONG_ANGLE_DEFAULT] = 22.5
    if c4d.GetC4DVersion() > 22600:
        objImport[c4d.OBJIMPORTOPTIONS_IMPORT_UVS] = c4d.OBJIMPORTOPTIONS_UV_ORIGINAL
    else:
        objImport[c4d.OBJEXPORTOPTIONS_TEXTURECOORDINATES] = True

    objImport[c4d.OBJIMPORTOPTIONS_SPLITBY] = c4d.OBJIMPORTOPTIONS_SPLITBY_OBJECT
    objImport[c4d.OBJIMPORTOPTIONS_MATERIAL] = c4d.OBJIMPORTOPTIONS_MATERIAL_MTLFILE
    objImport[c4d.OBJIMPORTOPTIONS_POINTTRANSFORM_FLIPZ] = True

    # Finally imports without dialogs
    if not c4d.documents.MergeDocument(doc, selectedFile, c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS, None):
        raise RuntimeError("Failed to load the document.")

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
