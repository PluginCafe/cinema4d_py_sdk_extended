"""
Copyright: MAXON Computer GmbH
Author: Joey Gaspe

Description:
    - Exports Obj with custom settings.

Class/method highlighted:
    - c4d.plugins.FindPlugin()
    - MSG_RETRIEVEPRIVATEDATA
    - c4d.documents.SaveDocument()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Retrieves a path to save the exported file
    filePath = c4d.storage.LoadDialog(title="Save File for OBJ Export", flags=c4d.FILESELECT_SAVE, force_suffix="obj")
    if not filePath:
        return

    # Retrieves Obj export plugin, defined in R17 as FORMAT_OBJ2EXPORT and below R17 as FORMAT_OBJEXPORT
    objExportId = c4d.FORMAT_OBJEXPORT if c4d.GetC4DVersion() < 17000 else c4d.FORMAT_OBJ2EXPORT
    plug = c4d.plugins.FindPlugin(objExportId, c4d.PLUGINTYPE_SCENESAVER)
    if plug is None:
        raise RuntimeError("Failed to retrieve the OBJ exporter.")

    data = dict()
    # Sends MSG_RETRIEVEPRIVATEDATA to OBJ export plugin
    if not plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, data):
        raise RuntimeError("Failed to retrieve private data.")

    # BaseList2D object stored in "imexporter" key hold the settings
    objExport = data.get("imexporter", None)
    if objExport is None:
        raise RuntimeError("Failed to retrieve BaseContainer private data.")

    # Defines OBJ export settings
    if c4d.GetC4DVersion() > 22600:
        objExport[c4d.OBJEXPORTOPTIONS_EXPORT_UVS] = c4d.OBJEXPORTOPTIONS_UV_ORIGINAL
    else:
        objExport[c4d.OBJEXPORTOPTIONS_TEXTURECOORDINATES] = True
    objExport[c4d.OBJEXPORTOPTIONS_MATERIAL] = c4d.OBJEXPORTOPTIONS_MATERIAL_MATERIAL

    # Finally export the document
    if not c4d.documents.SaveDocument(doc, filePath, c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST, objExportId):
        raise RuntimeError("Failed to save the document.")

    print("Document successfully exported to:", filePath)


if __name__ == '__main__':
    main()
