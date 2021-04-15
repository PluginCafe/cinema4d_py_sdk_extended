"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Retrieves the active Render Data (Render Settings).
    - Prints the Render Engine ID.

Class/method highlighted:
    - BaseDocument.GetActiveRenderData()
    - c4d.documents.RenderData

"""
import c4d


def main():
    # Retrieves the Active Render Data (Render Settings)
    renderData = doc.GetActiveRenderData()
    if renderData is None:
        raise RuntimeError("Failed to retrieve the active render data.")

    # Print the Active Render Engine ID, default cinema 4D render Id are:
    #   RDATA_RENDERENGINE_STANDARD = Standard
    #   RDATA_RENDERENGINE_PHYSICAL = Physical Render
    #   RDATA_RENDERENGINE_PREVIEWSOFTWARE = Software OpenGL
    #   RDATA_RENDERENGINE_PREVIEWHARDWARE = Hardware OpenGL
    #   RDATA_RENDERENGINE_GPURENDERER = Pro Render
    print(renderData[c4d.RDATA_RENDERENGINE])


if __name__ == "__main__":
    main()
