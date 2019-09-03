"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Renders a BaseDocument and saves the resulting image using a filename handling tokens.

Class/method highlighted:
    - c4d.modules.tokensystem.StringConvertTokens()

Compatible:
    - Win / Mac
    - R17, R18, R19, R20, R21
"""
import c4d


def main():
    # Initialize a Bitmap, to store our render results
    bitmap = c4d.bitmaps.BaseBitmap()
    if bitmap is None:
        raise MemoryError("Failed to create a BaseBitmap.")
    if bitmap.Init(1280, 720) != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    # Defines X/Y resolution of the render in the render setting
    renderData = doc.GetActiveRenderData()
    if renderData is None:
        raise RuntimeError("Failed to retrieve the render setting.")
    renderSettings = renderData.GetData()
    renderSettings[c4d.RDATA_XRES] = 1280
    renderSettings[c4d.RDATA_YRES] = 720

    # Reads the path stored in the render setting
    path = renderSettings[c4d.RDATA_PATH]

    # Renders the documents
    if c4d.documents.RenderDocument(doc, renderSettings, bitmap, c4d.RENDERFLAGS_NODOCUMENTCLONE, None) != c4d.RENDERRESULT_OK:
        raise RuntimeError("Failed to render the document.")

    # Tokenizes the path from the render engine
    rpd = {'_doc': doc, '_rData': renderData, '_rBc': renderSettings, '_frame': 1}
    finalFilename = c4d.modules.tokensystem.StringConvertTokens(path, rpd) + ".png"

    # Saves the render result to the tokenized file name
    bitmap.Save(finalFilename, c4d.FILTER_PNG)
    
    # Displays the saved picture into the picture viewer
    c4d.bitmaps.ShowBitmap(bitmap)


if __name__ == '__main__':
    main()