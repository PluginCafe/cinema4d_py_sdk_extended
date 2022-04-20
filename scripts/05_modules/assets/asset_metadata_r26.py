#coding: utf-8
"""Provides examples for reading and writing asset metadata.

Topics:
    * Accessing data in asset descriptions.
    * Reading an writing asset metadata.
    * Adding versions to assets.
    * Generating asset identifiers.
    * maxon.AssetDescription
    * maxon.AssetMetaData

Examples:
    * AccessAssetDescriptionData(): Accesses the data attached to an asset description.
    * AddAssetVersion(): Adds a version to a file asset of subtype object.
    * GenerateAssetIdentifiers(): Demonstrates how to generate asset identifiers.
    * IterateAssetMetadata(): Iterates over all existing entries in an AssetMetadata instance.
    * ReadAssetMetadata(): Reads the metadata of an asset that is commonly required to be read.
    * WriteAssetMetadata(): Writes the metadata of an asset that is commonly required to be written.
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2022 MAXON Computer GmbH"
__date__ = "10/03/2022"
__license__ = "Apache-2.0 License"
__version__ = "R26"

from typing import Tuple
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

def GetCableUsbAssetDescription() -> maxon.AssetDescription:
    """Is a helper function returning the asset description for the "Cable - USB" file object asset.

    The asset description for that asset is used by multiple examples in this file.
    """
    # Get the user preferences repository as the repository to store the new asset in.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    # The id of the "Cable - USB" asset.
    cableUsbId = maxon.Id("file_d0a26639c950371a")

    # Retrieve the asset description for the asset.
    assetDescription = repository.FindLatestAsset(
        maxon.AssetTypes.File(), cableUsbId, maxon.Id(), maxon.ASSET_FIND_MODE.LATEST)
    if assetDescription is None:
        raise RuntimeError("Could not find the 'Cable - USB' asset.")

    return assetDescription


# --- Start of Examples ----------------------------------------------------------------------------

def AccessAssetDescriptionData():
    """Accesses the data attached to an asset description.

    Highlights the meta information provided by an asset description for its asset that is not
    being accessed with the asset metadata container.
    """
    # Get the asset description for the "Cable - USB" file object asset.
    assetDescription = GetCableUsbAssetDescription()

    # The most important properties of an asset are its id, uniquely identifying the asset within
    # its database, the type id, denoting the kind of asset it is, and the URL, pointing to the
    # location of the primary data of the asset.
    assetId = assetDescription.GetId()
    assetTypeId = assetDescription.GetTypeId()
    assetUrl = assetDescription.GetUrl()
    print(f"Asset ID: {assetId}")
    print(f"Asset Type ID: {assetTypeId}")
    print(f"Asset URL: {assetUrl}")

    # Assets can have multiple versions which all then share intentionally the same id. The version
    # of an asset description is also stored in its metadata, but can more easily be accessed with
    # GetVersion() and GetVersionAndId. With the later returning an identifier that allows to
    # distinguish multiple versions of an asset.
    assetVersion = assetDescription.GetVersion()
    assetIdVersion = assetDescription.GetIdAndVersion()
    print(f"Asset Version: {assetVersion}")
    print(f"Asset IdAndVersion: {assetIdVersion}")

    # Important properties of an asset are also its repository and metadata container. The latter
    # contains most of the descriptive and administrative metadata associated with an asset.
    assetRepository = assetDescription.GetRepository()
    assetRepositoryId = assetDescription.GetRepositoryId()
    assetMetadata = assetDescription.GetMetaData()
    print(f"Asset Repository ID: {assetRepositoryId}")
    print(f"Asset Metadata: {assetMetadata}")

    # Also the reference to the AssetInterface for an asset description can be be loaded. It
    # provides access to more data (which overlaps with the data exposed in the asset description)
    # and gives access to the asset implementation. The UpdatePreviewThumbnail() example for the
    # dots preset asset type implementation provides a usage scenario for both accessing the base
    # and type specific asset interface to call the asset implementation. In non-implementation
    # usage both the base and type specific asset interface of an asset have to be accessed only
    # rarely.
    asset = assetDescription.Load()
    print(f"Loaded asset interface: {type(asset)}")
    print(f"Asset Type ID (via asset interface): {asset.GetTypeId()}")

    # When necessary, the asset interface can be cast to its type specific asset interface.
    if assetTypeId == maxon.AssetTypes.File().GetId():
        # Cast the generic base asset interface #asset for #assetDescription returned by #Load()
        # into its asset type specific type, a FileAsset in this case.
        fileAsset = maxon.Cast(maxon.FileAsset, asset)
        if not fileAsset:
            raise RuntimeError(f"Could not cast {asset} to a FileAsset.")
        print(f"FileAsset interface for {asset.GetId()}: {type(fileAsset)}")


def AddAssetVersion(doc: c4d.documents.BaseDocument):
    """Adds a version to a file asset of subtype object.

    A version of an asset is an asset that is stored under the same identifier as another asset but
    a different version. Such assets will be displayed as a singular asset in the Asset Browser and
    the different versions of the asset are only accessible in the 'Info Panel' of the Asset
    Browser. When that asset is loaded, and not specified differently, always the most recent
    version of the asset is loaded. Different versions of an asset must match in type but can
    otherwise be entirely different. The example adds an asset version to object assets that only
    contains a parametric sphere, overwriting all other content in the most recent version of the
    target asset.
    """
    if not isinstance(doc, c4d.documents.BaseDocument):
        raise TypeError(
            f"Expected {c4d.documents.BaseDocument} for 'doc'. Received: {doc}")

    # --- Creating the Original Asset --------------------------------------------------------------

    # The original asset will be created for the active object in the passed document. It will later
    # be shadowed by the asset version placed on top of it.

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
    storeAssetStruct = maxon.StoreAssetStruct(
        assetCategoryId, repository, repository)

    # Use the convenience method AssetCreationInterface.CreateObjectAsset() to create and store an
    # object asset in one operation. The instantiation of a FileAsset for the object is hidden
    # away, and instead we deal directly with the AssetDescription which is representing the object
    # file asset.
    assetDescription = maxon.AssetCreationInterface.CreateObjectAsset(
        obj, doc, storeAssetStruct, assetId, assetName, assetVersion, assetMetadata, True)

    # --- Creating the Asset Version ---------------------------------------------------------------

    # The asset version can be sourced from the same or a different document as shown here.
    tempDoc = c4d.documents.BaseDocument()

    # The asset version will overwrite all primary object asset data with a new object, a red sphere
    # in this example : Create the sphere object, a red material, insert them into #temDoc, and
    # create a texture tag, linking the material to the sphere object.
    sphere = c4d.BaseObject(c4d.Osphere)
    material = c4d.BaseMaterial(c4d.Mmaterial)
    material[c4d.MATERIAL_COLOR_COLOR] = c4d.Vector(1, 0, 0)

    tempDoc.InsertObject(sphere)
    tempDoc.InsertMaterial(material)

    textureTag = sphere.MakeTag(c4d.Ttexture)
    textureTag[c4d.TEXTURETAG_MATERIAL] = material

    # IMPORTANT: The asset id of an asset version is identical to the asset it should shadow.
    assetId = assetDescription.GetId()

    # The asset version, it could also be manually curated as it was for the original asset, e.g.,
    # "V2", but to avoid name collisions, it is safer to also use an UUID for the asset version.
    # In this case no prefix is required and a short UUID should be enough.
    assetVersion = maxon.AssetInterface.MakeUuid("", compact=True)

    # From here on out, everything is the same as for creating a new asset.
    assetName = f"Python SDK - Versioned Sphere Asset"
    assetCategoryId = maxon.Id("net.maxon.assetcategory.uncategorized")
    storeAssetStruct = maxon.StoreAssetStruct(
        assetCategoryId, repository, repository)

    # Passing a new asset metadata instance will shadow all asset metadata of the original asset.
    assetMetadata = maxon.AssetMetaData()

    # The asset version is stored under the same asset id as the asset(s) it is meant to shadow,
    # but with a different version identifier. Use could be here any method to store the asset,
    # e.g., #AssetRepositoryInterface.StoreAsset() would also work, as long as the shadowed asset
    # is of the same asset type (FileAsset in this case). The asset subtype (material, object, etc.)
    # could technically change (resulting in an asset that could be a material in its first
    # version but an object in its second version), but it is not advisable to do that to avoid
    # confusing users.
    assetVersionDescription = maxon.AssetCreationInterface.CreateObjectAsset(
        sphere, tempDoc, storeAssetStruct, assetId, assetName, assetVersion, assetMetadata, True)

    # See the "Versions" in the "Details" of the Asset Browser
    ShowAssetInBrowser(assetVersionDescription)
    print (f"Created asset for {obj} and overwrote the asset with version containing a sphere.")


def GenerateAssetIdentifiers():
    """Demonstrates how to generate asset identifiers.

    Asset identifiers (for non-versioned assets) must be unique within a repository without its
    bases. UUID-based identifiers generated by the operating system assure this quality but are
    also hard to reproduce at a later point of time or on another system. In some cases this quality
    of predictable asset identifiers is required to search for assets effectively or avoid ingesting
    duplicate assets. The example demonstrates with the cases of a category and image asset how such
    identifying asset hashes could be constructed.
    """
    # The common way to generate an asset identifier is AssetInterface.MakeUuid(), which calls the
    # OS specific UUID generators. The prefix passed to this function is not formally defined, but
    # it is good practice to pass in the lower-case name for the asset type. E.g., "category" for
    # CategoryAsset identifiers, "file" for FileAsset identifiers and so on.

    # Such id will be different every time it is being generated. When an asset with such an
    # identifier is being searched for in a repository, without its identifier being known
    # beforehand, the search must be conducted over the properties of the asset. Which is slower
    # and more labor-intensive then retrieving an asset description by its id.
    uuid = maxon.AssetInterface.MakeUuid("file", False)
    print(f"UUID identifier (different on each execution):{uuid}")

    # The alternative is to hash the identifier for an asset manually. A category asset identifier
    # could for example be hashed over its name and path; which will allow for predicting the id
    # of any category asset created in this manner:

    # Such asset id will be the same on each execution, but it will not allow multiple assets of
    # the same name to be attached to the same parent category, as they will resolve to the same
    # identifier. For such asset can be searched by 'predicting' its id over its known properties.
    categoryPath = r"MyStuff/Categories/Stone"
    hashInput = categoryPath.encode()

    # The native Python hashing libraries must be used to carry out the hashing, as the maxon
    # libraries in maxon.StreamConversions are not available in Python. Any hashing algorithm can
    # be used, but internally the Asset API makes use of MD5 when creating such 'predictable'
    # asset identifiers.
    import hashlib

    # The asset id should be prefixed by 'category' in this case since the asset will be a
    # CategoryAsset. There is a non-formal convention in the Asset API where automatically (UUID)
    # hashed assets will use the @ character for the prefix separator, while manually hashed assets
    # as this one, will use the _ character. This is primarily done to avoid name collisions between
    # UUID and manually hashed asset ids.
    hash = "category_" + hashlib.md5(hashInput).hexdigest()
    hashedAssetId = maxon.Id(hash)
    print(f"Category identifier hashed over its path: {hashedAssetId}")

    # A more complex example which does hash an image file asset over its origin file path,
    # resolution, and bit depth is shown below.
    assetUrl = maxon.Url("file://textures/stone/taking_things_for_granite.png")
    width, height, bitDepth = 4096, 4096, 32

    # There is no higher insight to be gained here, simply define a scheme for how the information
    # for such hash should be concatenated. Any form is fine, as long it is followed by all entities
    # which should be found under that scheme.
    hashInput = fr"{assetUrl}.{width}.{height}.{bitDepth}".encode()
    hash = "file_" + hashlib.md5(hashInput).hexdigest()
    hashedAssetId = maxon.Id(hash)
    print(f"Media image asset identifier hashed over image properties: {hashedAssetId}")

    # In special cases the asset id can also be a human readable id, as for example how it is
    # employed by the asset category "uncategorized".
    uncategorizedId = maxon.Id("net.maxon.assetcategory.uncategorized")
    print(f"Human readable identifier: {uncategorizedId}")

    # When declaring such identifiers the inverted domain pattern common to all human readable
    # maxon.Id instances should be applied, with the first element after the second level domain
    # being "assetcategory", followed by the human readable identifier. Be careful not to introduce
    # name collisions within your domain.
    myId = maxon.Id("com.mycompany.myproduct.myhumanreableid")
    print(f"Recommended pattern for human readable identifiers: {myId}")


def IterateAssetMetadata():
    """Iterates over all existing entries in an AssetMetadata instance.
    """
    # Get the asset description for the "Cable - USB" file object asset.
    assetDescription = GetCableUsbAssetDescription()

    # Get the metadata from the asset description.
    metaData = assetDescription.GetMetaData()
    print(f"Metadata Entries for {assetDescription.GetId()}:")

    # Iterate over all entries. The method returns a maxon.BaseArray(maxon.Tuple), where the tuples
    # have the form (maxon.Id, AssetMetaDataInterface.KIND), denoting the key (first) and and
    # additional flags (second) for an entry. The value of an entry is not returned and must be
    # retrieved manually when required.
    for key, _ in metaData.GetExistingEntries():
        value = metaData.Get(key)
        print(f"{key}: {value}")


def ReadAssetMetadata():
    """Reads the metadata of an asset that is commonly required to be read.
    """
    # Get the asset description for the "Cable - USB" file object asset.
    assetDescription = GetCableUsbAssetDescription()

    print(f"Reading Asset Metadata for: {assetDescription}")

    # Get the metadata from the asset description.
    metadata = assetDescription.GetMetaData()
    # Get the language Cinema 4D is currently running in.
    currentLanguage = maxon.Resource.GetCurrentLanguage()

    # Get the name of the asset, i.e., the string that is representing the asset in the Asset
    # Browser. The name could also be retrieved directly from the metadata, but for metadata of
    # type string there is the convenience method GetMetaString() which simplifies handling
    # localized strings.
    name = assetDescription.GetMetaString(maxon.OBJECT.BASE.NAME, currentLanguage, "")
    print(f"\tName: {name}")

    # Get the annotation of the asset shown in the info panel of the Asset Browser.
    annotation = assetDescription.GetMetaString(maxon.OBJECT.BASE.ANNOTATIONS, currentLanguage, "")
    annotation = annotation.replace('\n', ' | ')
    print(f"\tAnnotation: {annotation}")

    # Get the time stamp of the asset, denoting the last time it has been modified.
    timeStamp = metadata.Get(maxon.ASSETMETADATA.ASSET_TIMESTAMP)
    print(f"\tTime Stamp: {timeStamp}")

    # Get the IDs of the keyword assets associated with an asset. Keywords can be split over system
    # defined and user defined keywords. This applies to assets stored in read-only repositories.
    keywords = metadata.Get(maxon.ASSETMETADATA.Keywords)
    userKeywords = metadata.Get(maxon.ASSETMETADATA.UserKeywords)
    print(f"\tKeywords: {keywords}")
    print(f"\tUser-Keywords: {userKeywords}")

    # Get the id of the category the asset is parented to.
    category = metadata.Get(maxon.ASSETMETADATA.Category)
    print(f"\tCategory: {category}")

    # When the name of an category or keyword is required, then the respective category or keyword
    # asset(s) must be retrieved to read their metadata.
    lookupRepo = maxon.AssetInterface.GetUserPrefsRepository()
    if not lookupRepo:
        raise RuntimeError("Could not retrieve user preferences repository.")

    categoryDescription = lookupRepo.FindLatestAsset(
        maxon.AssetTypes.Category().GetId(), category, maxon.Id(), maxon.ASSET_FIND_MODE.LATEST)

    categoryName = categoryDescription.GetMetaString(maxon.OBJECT.BASE.NAME, currentLanguage, "")
    print(f"\t\tCategory Name: {categoryName}")

    # Get the sub type of an asset. This currently only applies to File assets. The subtype of
    # a file asset expresses if it holds an object, material, scene, media image or media movie
    # asset, or if it is a plain file asset, e.g., a PDF.
    subtype = metadata.Get(maxon.ASSETMETADATA.SubType)
    print(f"\tSubtype: {subtype}")

    # There is also a sub-container of metadata entries called the meta-properties of an asset. It
    # contains more specific meta-information, as for example the total number of points for file
    # assets which contain geometry.
    metaProperties = metadata.Get(maxon.ASSETMETADATA.MetaProperties)
    print(f"\tMeta Properties: {type(metaProperties)}")

    # Get the point count from the asset MetaProperties.
    pointCount = metaProperties.Get(maxon.ASSET.METAPROPERTIES.C4DFILE.POINTCOUNT, -1)
    print(f"\t\tPoint Count: {pointCount}")


def WriteAssetMetadata():
    """Writes the metadata of an asset that is commonly required to be written.
    """
    # Get the asset description for the "Cable - USB" file object asset.
    sourceDescription = GetCableUsbAssetDescription()

    # We must create a copy of that asset since the assets delivered with the builtin asset database
    # are read-only.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    copyId = maxon.AssetInterface.MakeUuid("file", False)
    assetDescription = repository.CopyAsset(copyId, sourceDescription)

    print(f"Writing Asset Metadata for: {assetDescription}")

    # Get the language Cinema 4D is currently running in.
    currentLanguage = maxon.Resource.GetCurrentLanguage()

    # Unlike for asset metadata read operations, write operations cannot be invoked on the
    # AssetMetadata object itself, but must be carried out with the AssetDescription.
    # metadata = assetDescription.GetMetaData() # <- Not required for writing asset metadata.

    # Set the name of the asset. As for reading strings, for metadata entries of type string there
    # is a specialized function for writing localized string entries which hides away the container
    # holding the strings for all languages.
    assetDescription.StoreMetaString(
        maxon.OBJECT.BASE.NAME, "Hello World!", currentLanguage)

    # Set the annotation of the asset shown in the info panel of the Asset Browser.
    assetDescription.StoreMetaString(
        maxon.OBJECT.BASE.ANNOTATIONS, "Python SDK Annotation", currentLanguage)

    # Some metadata properties as keywords and categories have dedicated convenience functions
    # attached to their interfaces. Both could be written directly in the metadata, but it is
    # usually easier to use the convenience functions.

    # Set the category of the asset to the category "Asset API Examples" in the SDK-Database.
    categegoryId = maxon.Id("net.maxon.assetcategory.uncategorized")
    maxon.CategoryAssetInterface.SetAssetCategory(assetDescription, categegoryId)

    # Add the keyword "Abstract Shape" to the asset.
    keywordId = maxon.Id("keyword@05a41587b3094d08b77a5b6fbc61b4c6")
    maxon.KeywordAssetInterface.AddKeyword(
        assetDescription, keywordId, True, assetDescription.GetRepository())

    ShowAssetInBrowser(assetDescription)


if __name__ == "__main__":
    # AccessAssetDescriptionData()
    # AddAssetVersion(doc)
    # GenerateAssetIdentifiers()
    # IterateAssetMetadata()
    # ReadAssetMetadata()
    # WriteAssetMetadata()
    c4d.EventAdd()
