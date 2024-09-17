#coding: utf-8
"""Provides examples for creating and loading different asset types.

Topics:
    * Creating object, material, scene, media, and arbitrary file assets.
    * Creating category and keyword assets.
    * Link media assets in materials and loading assets back into a scene.
    * maxon.AssetCreationInterface
    * maxon.AssetManagerInterface.LoadAssets
    * maxon.StoreAssetStruct

Examples:
    * CreateObjectAsset(): Stores a BaseObject as an asset.
    * CreateMaterialAsset(): Stores a BaseMaterial as an asset.
    * CreateSceneAsset(): Stores a BaseDocument as an asset.
    * CreateMediaAsset(): Stores a texture or video file as a media asset.
    * CreateArbitraryFileAsset(): Stores an arbitrary file as an asset.
    * CreateCategoryAsset(): Creates a category asset.
    * CreateKeywordAsset(): Creates a keyword asset.
    * LinkMediaAssets(): Loads media assets as materials into the passed document.
    * LoadAssets(): Loads file and node template assets into the active document.

Note:
    Creating node template assets is currently not possible with the Python API, but loading them 
    back is.
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2022 MAXON Computer GmbH"
__date__ = "10/03/2022"
__license__ = "Apache-2.0 License"
__version__ = "R26"

import c4d
import maxon

# The command id for the Asset Browser.
CID_ASSET_BROWSER = 1054225


def ShowAssetInBrowser(asset: maxon.AssetDescription):
    """Provides a helper function used by the examples to reveal an asset in the Asset Browser.
    """
    if not isinstance(asset, maxon.AssetDescription):
        raise TypeError(f"Expected {maxon.AssetDescription} for 'asset'. Received: {asset}")

    # Open the Asset Browser when it is not already open.
    if not c4d.IsCommandChecked(CID_ASSET_BROWSER):
        c4d.CallCommand(CID_ASSET_BROWSER)

    # RevealAsset() can show more than one asset (even in multiple locations) which is why we
    # must wrap the asset to reveal in a list.
    maxon.AssetManagerInterface.RevealAsset([asset])

# --- Start of Examples ----------------------------------------------------------------------------

def CreateObjectAsset(doc: c4d.documents.BaseDocument):
    """Stores a BaseObject as an asset.

    The object is being stored with all 'connected' elements as child objects, tags, materials, and
    shaders. Uses the convenience function CreateObjectAsset() to simplify the process.
    """
    if not isinstance(doc, c4d.documents.BaseDocument):
        raise TypeError(f"Expected {c4d.documents.BaseDocument} for 'doc'. Received: {doc}")

    # Get the active object in the passed document.
    obj = doc.GetActiveObject()
    if obj is None:
        raise RuntimeError("There is no object selected in {doc}.")

    # Get the user preferences repository as the repository to store the new asset in.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    # Id, name, and version for the new object asset which will be created for #obj.
    assetId = maxon.AssetInterface.MakeUuid("object", False)
    assetName = f"Python SDK - Object Asset Example ({obj.GetName()})"
    assetVersion = "1.0"

    # The metadata of the asset, which are left empty in this example, and the category in which
    # the asset will be placed, the "Uncategorized" category in the Asset Browser.
    assetMetadata = maxon.AssetMetaData()
    assetCategoryId = maxon.Id("net.maxon.assetcategory.uncategorized")

    # A StoreAssetStruct is a helper data structure for storing assets which bundles up an asset
    # category and storage and lookup repository for the operation.
    storeAssetStruct = maxon.StoreAssetStruct(assetCategoryId, repository, repository)

    # Use the convenience method AssetCreationInterface.CreateObjectAsset() to create and store an
    # object asset in one operation. The instantiation of a FileAsset for the object is hidden
    # away, and instead we deal directly with the AssetDescription which is representing the object
    # file asset.
    assetDescription = maxon.AssetCreationInterface.CreateObjectAsset(
        obj, doc, storeAssetStruct, assetId, assetName, assetVersion, assetMetadata, True)

    print(f"Asset description for the asset for {obj}: {assetDescription}")

    # Reveal the newly created asset in the Asset Browser.
    ShowAssetInBrowser(assetDescription)


def CreateMaterialAsset(doc: c4d.documents.BaseDocument):
    """Stores a BaseMaterial as an asset.

    The material is being stored with all 'connected' shaders. Uses the convenience function
    CreateMaterialAsset() to simplify the process.
    """
    if not isinstance(doc, c4d.documents.BaseDocument):
        raise TypeError(
            f"Expected {c4d.documents.BaseDocument} for 'doc'. Received: {doc}")

    # Get the active material in the passed document.
    mat = doc.GetActiveMaterial()
    if mat is None:
        raise RuntimeError("There is no material selected in {doc}.")

    # Get the user preferences repository as the repository to store the new asset in.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    # Id, name, and version for the new material asset which will be created for #mat.
    assetId = maxon.AssetInterface.MakeUuid("material", False)
    assetName = f"Python SDK - Material Asset Example ({mat.GetName()})"
    assetVersion = "1.0"

    # The metadata of the asset, which are left empty in this example, and the category in which
    # the asset will be placed, the "Uncategorized" category in the Asset Browser.
    assetMetadata = maxon.AssetMetaData()
    assetCategoryId = maxon.Id("net.maxon.assetcategory.uncategorized")

    # A StoreAssetStruct is a helper data structure for storing assets which bundles up an asset
    # category and storage and lookup repository for the operation.
    storeAssetStruct = maxon.StoreAssetStruct(
        assetCategoryId, repository, repository)

    # Use the convenience method AssetCreationInterface.CreateMaterialAsset() to create and store a
    # material asset in one operation. The instantiation of a FileAsset for the material is hidden
    # away, and instead we deal directly with the AssetDescription which is representing the
    # material file asset.
    assetDescription = maxon.AssetCreationInterface.CreateMaterialAsset(
        doc, mat, storeAssetStruct, assetId, assetName, assetVersion, assetMetadata, True)

    print(f"Asset description for the asset for {mat}: {assetDescription}")

    # Reveal the newly created asset in the Asset Browser.
    ShowAssetInBrowser(assetDescription)


def CreateSceneAsset(doc: c4d.documents.BaseDocument):
    """Stores a BaseDocument as an asset.

    The scene is being stored with all its dependencies as objects, materials and shaders. Uses the
    convenience function CreateSceneAsset() to simplify the process.
    """
    if not isinstance(doc, c4d.documents.BaseDocument):
        raise TypeError(
            f"Expected {c4d.documents.BaseDocument} for 'doc'. Received: {doc}")

    # Get the user preferences repository as the repository to store the new asset in.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    # Id, name, and version for the new scene asset which will be created for #doc.
    assetId = maxon.AssetInterface.MakeUuid("scene", False)
    assetName = f"Python SDK - Scene Asset Example ({doc.GetDocumentName()})"
    assetVersion = "1.0"

    # The metadata of the asset, which are left empty in this example, and the category in which
    # the asset will be placed, the "Uncategorized" category in the Asset Browser.
    assetMetadata = maxon.AssetMetaData()
    assetCategoryId = maxon.Id("net.maxon.assetcategory.uncategorized")

    # A StoreAssetStruct is a helper data structure for storing assets which bundles up an asset
    # category and storage and lookup repository for the operation.
    storeAssetStruct = maxon.StoreAssetStruct(assetCategoryId, repository, repository)

    # Use the convenience method AssetCreationInterface.CreateSceneAsset() to create and store a
    # scene asset in one operation. The instantiation of a FileAsset for the scene is hidden
    # away, and instead we deal directly with the AssetDescription which is representing the scene
    # file asset.
    assetDescription = maxon.AssetCreationInterface.CreateSceneAsset(
        doc, storeAssetStruct, assetId, assetName, assetVersion, assetMetadata, True)

    print(f"Asset description for the asset for {doc}: {assetDescription}")

    # Reveal the newly created asset in the Asset Browser.
    ShowAssetInBrowser(assetDescription)


def CreateMediaAsset():
    """Stores a texture or video file as a media asset.

    Other than arbitrary file assets, media assets will have a preview thumbnail reflecting the
    specific content of the asset and open in the picture viewer when invoked in the Asset Browser.
    Uses the convenience function SaveTextureAsset to simplify the process.
    """
    # Open a directory selection dialog to let the user select a texture file.
    path = c4d.storage.LoadDialog(type=c4d.FILESELECTTYPE_IMAGES,
                                  title='Select an image file',
                                  flags=c4d.FILESELECT_LOAD)
    if path is None:
        return None

    # Wrap the path as a maxon.Url as the Maxon API only deals with file paths in this form.
    url = maxon.Url(path)

    # Get the user preferences repository as the repository to store the new asset in.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    # The name and category for the new asset.
    assetName = f"Python SDK - Media Asset Example ({url.GetName()})"
    assetCategoryId = maxon.Id("net.maxon.assetcategory.uncategorized")

    # A StoreAssetStruct is a helper data structure for storing assets which bundles up an asset
    # category and storage and lookup repository for the operation.
    storeAssetStruct = maxon.StoreAssetStruct(assetCategoryId, repository, repository)

    # Use the convenience method AssetCreationInterface.SaveTextureAsset() to create and store a
    # media asset in one operation. The instantiation of a FileAsset for the media file is hidden
    # away, and instead we deal directly with the AssetDescription which is representing the media
    # file asset.
    assetDescription, hasBeenSaved = maxon.AssetCreationInterface.SaveTextureAsset(
        url, assetName, storeAssetStruct, (), True)

    print(f"Asset description for the asset for {url}: {assetDescription}")

    # Reveal the newly created asset in the Asset Browser.
    ShowAssetInBrowser(assetDescription)


def CreateArbitraryFileAsset():
    """Stores an arbitrary file as an asset.

    Many forms of assets as scenes, objects, materials and textures are file type assets which are
    distinguished only by their asset subtype. File type assets can also have the empty id as their
    subtype, allowing them to wrap around arbitrary file types as for example a PDF or Word file.
    File assets of unsupported subtype lack the special handling of a supported subtype asset as
    for example preview images or loading them when double clicked. File assets should always be
    stored under the correct subtype, and only assets for unsupported file types should be stored
    as plain file assets. Uses the convenience function SaveMemFileAsAssetWithCopyAsset which will
    make a copy of the file to be stored as an asset in the asset database.

    """
    # Open a directory selection dialog to let the user select a texture file.
    path = c4d.storage.LoadDialog(type=c4d.FILESELECTTYPE_ANYTHING,
                                  title='Select any file',
                                  flags=c4d.FILESELECT_LOAD)
    if path is None:
        return None

    # Wrap the path as a maxon.Url as the Maxon API only deals with file paths in this form.
    url = maxon.Url(path)

    # Get the user preferences repository as the repository to store the new asset in.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    # The name and category for the new asset.
    assetName = f"Python SDK - File Asset Example ({url.GetName()})"
    assetCategoryId = maxon.Id("net.maxon.assetcategory.uncategorized")

    # The subtype of the asset, since the goal is here to store a FileAsset without a subtype,
    # the id will be left empty.
    assetSubtypeId = maxon.InternedId()

    # A StoreAssetStruct is a helper data structure for storing assets which bundles up an asset
    # category and storage and lookup repository for the operation.
    storeAssetStruct = maxon.StoreAssetStruct(
        assetCategoryId, repository, repository)

    # Use the convenience method AssetCreationInterface.SaveMemFileAsAssetWithCopyAsset() to create
    # and store a file asset without a subtype in one operation. The instantiation of a FileAsset
    # for the file is hidden away, and instead we deal directly with the AssetDescription which is
    # representing the file asset.
    assetDescription, hasBeenSaved = maxon.AssetCreationInterface.SaveMemFileAsAssetWithCopyAsset(
        url, storeAssetStruct, assetSubtypeId, (), assetName, False)

    print(f"Asset description for the asset for {url}: {assetDescription}")

    # Reveal the newly created asset in the Asset Browser.
    ShowAssetInBrowser(assetDescription)


def CreateCategoryAsset():
    """Creates a category asset.

    Asset categories are the folder structure visible in the Asset Browser that group other asset.
    Each of these categories is an asset itself and each asset, including category assets
    themselves, can reference exactly one category asset as its parent category.
    """
    # Get the user preferences repository as the repository to store the new asset in.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    # Instantiate a new category asset and create an asset id for it.
    categoryAsset = maxon.CategoryAsset().Create()
    assetId = maxon.AssetInterface.MakeUuid("category", False)

    # Store the asset. This raises an error when the operations fails. Against our Cinema API
    # Python instincts, we do not have to check here if the operation was successful in the maxon
    # API. When some special error handling is required, a try/except/else/finally block must be
    # used. See EraseAsset() for an example.
    assetDescription = repository.StoreAsset(assetId, categoryAsset)

    # Get the language Cinema 4D is currently running in.
    language = maxon.Resource.GetCurrentLanguage()

    # Set the name of the newly created asset, i.e., the name of the category.
    name = "Python SDK Category"
    assetDescription.StoreMetaString(maxon.OBJECT.BASE.NAME, name, language)

    # Parent the asset, a category, to the uncategorized category.
    categoryId = maxon.Id("net.maxon.assetcategory.uncategorized")
    maxon.CategoryAssetInterface.SetAssetCategory(assetDescription, categoryId)

    print(f"Asset description for the asset for '{name}': {assetDescription}")

    # Reveal the newly created asset in the Asset Browser.
    ShowAssetInBrowser(assetDescription)


def CreateKeywordAsset():
    """Creates a keyword asset.

    Asset keywords are used by the Asset Browser to group assets in addition to categories. Each
    keyword is an asset itself which can be referenced with its asset id by other assets as one of
    their multiple keywords.
    """
    # Get the user preferences repository as the repository to store the new asset in.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    # Instantiate a new keyword asset and create an asset id for it.
    keywordAsset = maxon.KeywordAssetInterface().Create()
    assetId = maxon.AssetInterface.MakeUuid("keyword", False)

    # Store the asset. This raises an error when the operations fails. Against our Cinema API
    # Python instincts, we do not have to check here if the operation was successful in the maxon
    # API. When some special error handling is required, a try/except/else/finally block must be
    # used. See EraseAsset() for an example.
    assetDescription = repository.StoreAsset(assetId, keywordAsset)

    # Get the language Cinema 4D is currently running in.
    language = maxon.Resource.GetCurrentLanguage()

    # Set the name of the newly created asset, i.e., the name of the category.
    name = "Python SDK Keyword"
    assetDescription.StoreMetaString(maxon.OBJECT.BASE.NAME, name, language)

    print(f"Asset description for the asset for '{name}': {assetDescription}")


def LinkMediaAssets(doc: c4d.documents.BaseDocument):
    """Loads media assets as materials into the passed document.

    Loads five texture assets from "tex/Surfaces/Stone" as the color channel of five new materials
    into the passed document. The major insight of this example is that the URL of a media file
    asset can be used directly to access its content.
    """
    # See AdvancedAssetSearch() in asset_databases.py for an introduction in asset searches and the
    # specifics of variable access of inner functions.

    # This is a more complex asset search case as shown in AdvancedAssetSearch() in
    # asset_datbases.py. Instead of just appending all encountered assets to an output
    # list, only assets which are parented to the category "tex/Surfaces/Stone" will be appended,
    # and after five assets have been found, the search will be terminated. This is such case where
    # a new object must be assigned to an outer variable. It is here the counter variable
    # #numberOfAssetsToFind which is reassigned by the callback function GetFiveStoneMediaAssets()
    # with the operation:
    #
    #   `callbackData["numberOfAssetsToFind"] -= 1`
    callbackData = {
        # The "tex/Surfaces/Stone" category of the builtin asset database.
        "stoneCategory": maxon.Id("category@f089b9955a4f4b619bb9cd836c7296f1"),
        # The maximum number of assets to find and the value reassigned by GetFiveStoneMediaAssets()
        "numberOfAssetsToFind": 5,
        # The list to append the first five stone media assets to the callback gets passed.
        "stoneMediaAssets": []
    }

    def GetFiveStoneMediaAssets(assetDescription: maxon.AssetDescription) -> bool:
        """Callback function to find five media assets in the category "tex/Surfaces/Stone".
        """
        # Exit the search when the maximum number of assets has already been found. This is only
        # a safety measure and should never evaluate as #True.
        if callbackData["numberOfAssetsToFind"] < 1:
            return False

        # Get the metadata, subtype and parent category of the asset.
        assetMetadata = assetDescription.GetMetaData()
        asssetSubtype = assetMetadata.Get(maxon.ASSETMETADATA.SubType, maxon.Id())
        parentCategory = maxon.CategoryAsset.GetParentCategory(
            assetDescription)

        # This not an asset parented to "tex/Surfaces/Stone"
        if parentCategory != callbackData["stoneCategory"]:
            return True

        # This is not a media asset.
        if not (asssetSubtype in (maxon.ASSETMETADATA.SubType_ENUM_MediaImage,
                                  maxon.ASSETMETADATA.SubType_ENUM_MediaMovie)):
            return True

        # This is a matching asset.
        callbackData["stoneMediaAssets"].append(assetDescription)
        callbackData["numberOfAssetsToFind"] -= 1

        # Terminate the search when the maximum number of assets has been found, otherwise continue.
        return callbackData["numberOfAssetsToFind"] > 0

        # --- End of Inner Function Scope ----------------------------------------------------------

    # Get the language Cinema 4D is currently running in.
    language = maxon.Resource.GetCurrentLanguage()
    # Get the user preferences repository as the repository to load assets from.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    repository.FindAssets(maxon.AssetTypes.File().GetId(), maxon.Id(), maxon.Id(),
                          maxon.ASSET_FIND_MODE.LATEST, GetFiveStoneMediaAssets)

    # Create materials for the found stone texture assets.
    for assetDescription in callbackData["stoneMediaAssets"]:

        # Get the string with which the asset is labelled in the Asset Browser.
        assetName = assetDescription.GetMetaString(
            maxon.OBJECT.BASE.NAME, language, "Default Asset Name")

        # Get the URL of the asset, the location of the media file.
        url = assetDescription.GetUrl()

        # Test if the URL is the empty URL, i.e., "". This should not happen normally.
        if url.IsEmpty():
            raise RuntimeError("Encountered asset with the empty URL.")

        # Instantiate a material and a bitmap shader, and insert the shader into the material.
        material = c4d.BaseMaterial(c4d.Mmaterial)
        if material is None:
            raise MemoryError("Could not allocate material.")

        shader = c4d.BaseShader(c4d.Xbitmap)
        if shader is None:
            raise MemoryError("Could not allocate material.")

        material.InsertShader(shader)

        # Link the shader in the color channel of the material and set the asset url as the file
        # of the bitmap shader.
        material[c4d.MATERIAL_COLOR_SHADER] = shader
        shader[c4d.BITMAPSHADER_FILENAME] = str(url)

        # Name the material after the asset and insert it into the passed document.
        assetName = assetDescription.GetMetaString(maxon.OBJECT.BASE.NAME, language, "")
        material.SetName(f"Python SDK Material({assetName})")
        doc.InsertMaterial(material)

def LoadAssets(doc: c4d.documents.BaseDocument):
    """Loads file and node template assets into the active document.

    Uses the convenience function AssetManagerInterface.LoadAssets to load asset back. The function
    will always target the active document. When assets should be loaded into a document that is
    not the active document, the  asset must be loaded manually over the URL of the asset.
    """
    def GetSceneNodesGraph(doc: c4d.documents.BaseDocument) -> maxon.NodesGraphModelRef:
        """Returns the Scene Nodes graph of the active document.
        """
        # Get the scene nodes scene hook.
        sceneNodesHook = doc.FindSceneHook(c4d.SCENENODES_IDS_SCENEHOOK_ID)
        if not sceneNodesHook:
            raise RuntimeError("Could not retrieve Scene Nodes scene hook.")

        # Get the scene nodes graph from the hook.
        sceneNodesHook.Message(maxon.neutron.MSG_CREATE_IF_REQUIRED)
        sceneNodes = sceneNodesHook.GetNimbusRef("net.maxon.neutron.nodespace")
        if not sceneNodes:
            raise RuntimeError("Could not retrieve Scene Nodes graph model.")

        graph = sceneNodes.GetGraph()
        if graph.IsReadOnly():
            raise RuntimeError("Scene Nodes graph is read only.")

        return graph

    # Get the user preferences repository as the repository to load assets from.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    # The id of the "Car Paint - Red - Flakes" material asset.
    materialAssetId = maxon.Id("file_c59cb9cb4d67f269")
    # The id of the "Cable - USB" object asset.
    objectAssetId = maxon.Id("file_d0a26639c950371a")
    # The id of the "Beach - Low Poly.c4d" scene asset.
    sceneAssetId = maxon.Id("file_86d7094366bd57c5")

    # The id of the "Cube" scene node template which is also the asset id of the node.
    sceneNodeTemplateId = maxon.Id("net.maxon.neutron.node.primitive.cube")

    # To load assets back, the method AssetMangerInterface.LoadAssets can be used. The major 
    # argument is the second argument which accepts a list of asset id, filter string tuples.
    # The tuples are only relevant in the context of node templates. The method can load multiple
    # assets at once into the active document.
    assetsToLoad = [(materialAssetId, ""), (objectAssetId, "")]
    didLoad = maxon.AssetManagerInterface.LoadAssets(repository, assetsToLoad)
    if not didLoad:
        raise RuntimeError(f"Could not load assets for the ids: {assetsToLoad}")

    # Load the "cube" node template into the Scene Nodes graph of the active document.
    didLoad = maxon.AssetManagerInterface.LoadAssets(
        repository, [(sceneNodeTemplateId, "")], graphModelRef=GetSceneNodesGraph(doc))
    if not didLoad:
        raise RuntimeError(f"Could not load assets for the ids: {sceneNodeTemplateId}")

    # Other than for other asset types, scene assets will always be loaded into a new document.
    didLoad = maxon.AssetManagerInterface.LoadAssets(repository, [(sceneAssetId, "")])
    if not didLoad:
        raise RuntimeError(f"Could not load assets for the ids: {sceneAssetId}")
    

if __name__ == "__main__":
    CreateObjectAsset(doc)
    CreateMaterialAsset(doc)
    CreateSceneAsset(doc)
    CreateMediaAsset()
    CreateArbitraryFileAsset()
    CreateCategoryAsset()
    CreateKeywordAsset()
    LinkMediaAssets(doc)
    LoadAssets(doc)
    c4d.EventAdd()
