# Asset API

Provide content as reusable assets served with the Cinema 4D Asset Browser.

## Introduction

The Asset API is a collection of interfaces for the Asset Browser, replacing the older Content Browser. The API does provide only limited access to the graphical user interface of the Asset Browser and primarily exposes the underlying data structures that are represented by the Asset Browser.

Assets come natively in the form of scenes, objects, materials, media files, presets and other minor types as category and keyword assets. This data wrapped by an asset can be loaded into a scene with the Asset Browser and is stored in asset databases. Asset databases also store metadata for all their assets. This asset metadata is accessible in its most tangible form in the Info Area of the Asset Browser, displaying for example an annotation which describes a single asset.

## Asset Databases and Repositories

The file `asset_databases_r26.py` provides examples for handling asset databases and repositories.

###### Topics
* Mounting and unmounting of asset databases.
* Retrieving asset repositories.
* Storing, copying, erasing, and searching assets.
* `maxon.AssetDataBasesInterface`
* `maxon.AssetRepositoryInterface`
* `maxon.AssetDatabaseStruct`

###### Examples
* `MountAssetDatabase()`: Mounts a local directory as an asset database into Cinema 4D, making its 
assets available in the Asset Browser.
* `UnmountAssetDatabase()`: Unmounts an asset database from Cinema 4D, making its assets 
unavailable in the Asset Browser.
* `AccessUserDatabases()`: Accesses the data structures representing the user asset databases.
* `GetImportantRepositories()`: Accesses the builtin, application, user preferences and active document repositories.
* `CreateRepositories()`: Creates repositories for all user databases.
* `StoreAsset()`: Stores an asset instance in a repository.
* `CopyAsset()`: Copies an asset in a repository to another asset.
* `EraseAsset()`: Removes an asset from an asset repository permanently.
* `SimpleAssetSearch()`: Performs a simple search operation for assets by their type, id or version.
* `AdvancedAssetSearch()`: Performs an advanced search evaluating the metadata of the searched assets.
* `SortAssets()`: Sorts assets by their metadata properties.

## Asset Types

The file `asset_types_r26.py` provides examples for creating and loading different asset types.

###### Topics
* Creating object, material, scene, media, and arbitrary file assets.
* Creating category and keyword assets.
* Link media assets in materials and loading assets back into a scene.
* `maxon.AssetCreationInterface`
* `maxon.AssetManagerInterface.LoadAssets()`
* `maxon.StoreAssetStruct`

> :warning: Creating node template assets is currently not possible with the Python API, but loading them back is.

###### Examples
* `CreateObjectAsset()`: Stores a BaseObject as an asset.
* `CreateMaterialAsset()`: Stores a BaseMaterial as an asset.
* `CreateSceneAsset()`: Stores a BaseDocument as an asset.
* `CreateMediaAsset()`: Stores a texture or video file as a media asset.
* `CreateArbitraryFileAsset()`: Stores an arbitrary file as an asset.
* `CreateCategoryAsset()`: Creates a category asset.
* `CreateKeywordAsset()`: Creates a keyword asset.
* `LinkMediaAssets()`: Loads media assets as materials into the passed document.
* `LoadAssets()`: Loads file and node template assets into the active document.

## Asset Metadata
The file `asset_metadata_r26.py` provides examples for reading and writing asset metadata.

###### Topics
* Accessing data in asset descriptions.
* Reading an writing asset metadata.
* Adding versions to assets.
* Generating asset identifiers.
* `maxon.AssetDescription`
* `maxon.AssetMetaData`

###### Examples
* `AccessAssetDescriptionData()`: Accesses the data attached to an asset description.
* `AddAssetVersion()`: Adds a version to a file asset of subtype object.
* `GenerateAssetIdentifiers()`: Demonstrates how to generate asset identifiers.
* `IterateAssetMetadata()`: Iterates over all existing entries in an AssetMetadata instance.
* `ReadAssetMetadata()`: Reads the metadata of an asset that is commonly required to be read.
* `WriteAssetMetadata()`: Writes the metadata of an asset that is commonly required to be written.
