"""
Copyright: MAXON Computer GmbH

Description:
    - Exports Alembic with custom settings.

Class/method highlighted:
    - c4d.plugins.FindPlugin()
    - MSG_RETRIEVEPRIVATEDATA
    - c4d.documents.SaveDocument()

Compatible:
    - Win / Mac
    - R14, R15, R16, R17, R18, R19, R20, R21, S22, R23
"""
import c4d


def main():
    # Retrieves a path to save the exported file
    filePath = c4d.storage.LoadDialog(title="Save File for Alembic Export", flags=c4d.FILESELECT_SAVE, force_suffix="abc")
    if not filePath:
        return

    # Retrieves Alembic exporter plugin, 1028082, defined in R20.046 as FORMAT_ABCEXPORT
    abcExportId = 1028082 if c4d.GetC4DVersion() < 20046 else c4d.FORMAT_ABCEXPORT
    plug = c4d.plugins.FindPlugin(abcExportId, c4d.PLUGINTYPE_SCENESAVER)
    if plug is None:
        raise RuntimeError("Failed to retrieve the alembic exporter.")

    data = dict()
    # Sends MSG_RETRIEVEPRIVATEDATA to Alembic export plugin
    if not plug.Message(c4d.MSG_RETRIEVEPRIVATEDATA, data):
        raise RuntimeError("Failed to retrieve private data.")

    # BaseList2D object stored in "imexporter" key hold the settings
    abcExport = data.get("imexporter", None)
    if abcExport is None:
        raise RuntimeError("Failed to retrieve BaseContainer private data.")

    # Defines Alembic export settings
    abcExport[c4d.ABCEXPORT_SELECTION_ONLY] = True
    abcExport[c4d.ABCEXPORT_PARTICLES] = False
    abcExport[c4d.ABCEXPORT_PARTICLE_GEOMETRY] = False

    # Finally export the document
    if not c4d.documents.SaveDocument(doc, filePath, c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST, abcExportId):
        raise RuntimeError("Failed to save the document.")

    print("Document successfully exported to:", filePath)


if __name__ == '__main__':
    main()
