#coding: utf-8
"""Provides examples for handling asset databases and repositories.

The form of storing assets shown here with StoreAsset() is very atomic and not commonly used for
complex asset types. See asset_types.py for examples for these more commonly used methods.

Topics:
    * Mounting and unmounting of asset databases.
    * Retrieving asset repositories.
    * Storing, copying, erasing, and searching assets.
    * maxon.AssetDataBasesInterface
    * maxon.AssetRepositoryInterface
    * maxon.AssetDatabaseStruct

Examples:
    * MountAssetDatabase(): Mounts a local directory as an asset database into Cinema 4D, making its
    assets available in the Asset Browser.
    * UnmountAssetDatabase(): Unmounts an asset database from Cinema 4D, making its assets
    unavailable in the Asset Browser.
    * AccessUserDatabases(): Accesses the data structures representing the user asset databases.
    * GetImportantRepositories(): Accesses the builtin, application, user preferences and active
    document repositories.
    * CreateRepositories(): Creates repositories for all user databases.
    * StoreAsset(): Stores an asset instance in a repository.
    * CopyAsset(): Copies an asset in a repository to another asset.
    * EraseAsset(): Removes an asset from an asset repository permanently.
    * SimpleAssetSearch(): Performs a simple search operation for assets by their type, id or
     version.
    * AdvancedAssetSearch():"Performs an advanced search evaluating the metadata of the searched
    assets.
    * SortAssets(): Sorts assets by their metadata properties.
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


def MountAssetDatabase():
    """Mounts a local directory as an asset database into Cinema 4D, making its assets available
    in the Asset Browser.

    The functionality of this example is very similar to what is being provided by the "Add Folder"
    button in the Asset Browser section of the Preferences dialog of Cinema 4D. Check the
    dialog after running the example, it will then contain the added database. The example will open
    a directory selection dialog for the user to select a directory which should be mounted and then
    mount that URL as an asset database. When the selected path is already mounted as an asset
    database, the data for the already mounted database will be returned. When the selected path
    does not contain an asset database, the necessary metadata will be created in that
    location by Cinema 4D.
    """
    # Wait for all asset databases to be loaded and abort when this is not possible.
    if not maxon.AssetDataBasesInterface.WaitForDatabaseLoading():
        return RuntimeError("Could not load asset databases.")

    # Open a directory selection dialog to let the user select a database path to mount.
    path = c4d.storage.LoadDialog(
        title='Select an asset database directory', flags=c4d.FILESELECT_DIRECTORY)
    if path is None:
        return None

    # Convert #path to a maxon.Url and get all currently mounted databases.
    url = maxon.Url(path)
    databaseCollection = maxon.AssetDataBasesInterface.GetDatabases()

    # Search the already mounted databases for a database that has the URL #url. When such database
    # does exist, ensure that it is active and return it instead of attempting to mount it again.
    for database in databaseCollection:
        if database._dbUrl == url:
            database._active = True
            maxon.AssetDataBasesInterface.SetDatabases(databaseCollection)
            print (f"Returning existing database for '{url}'.")
            return database

    # Construct a new database struct for the new database location, add the struct to the
    # collection of databases and mount them all. An AssetDatabaseStruct is only a surrogate for
    # an asset database and does not contain any data besides the URL of the database, if it is
    # active or not, and two additional fields of minor importance. Cinema 4D will create the
    # necessary asset database metadata at #url when #url is pointing to a location where no such
    # asset database metadata does exist. It is also important to add the new database to the
    # collection of all databases and then mount that collection, as otherwise all other asset
    # databases would be unmounted.
    newDatabase = maxon.AssetDatabaseStruct(url)
    databaseCollection.append(newDatabase)
    maxon.AssetDataBasesInterface.SetDatabases(databaseCollection)
    print (f"Created new database for '{url}'.")


def UnmountAssetDatabase():
    """Unmounts an asset database from Cinema 4D, making its assets unavailable in the Asset Browser.
    """
    # Wait for all asset databases to be loaded and abort when this is not possible.
    if not maxon.AssetDataBasesInterface.WaitForDatabaseLoading():
        return RuntimeError("Could not load asset databases.")

    # Open a directory selection dialog to let the user select a database path to unmount.
    path = c4d.storage.LoadDialog(
        title='Select an asset database directory to unmount.', flags=c4d.FILESELECT_DIRECTORY)
    if path is None:
        return None

    # Convert #path to a maxon.Url and get all currently mounted databases.
    url = maxon.Url(path)
    databaseCollection = maxon.AssetDataBasesInterface.GetDatabases()

    # Search the already mounted databases for a database that has the URL #url.
    for i, database in enumerate(databaseCollection):
        if database._dbUrl == url:
            databaseCollection.pop(i)
            maxon.AssetDataBasesInterface.SetDatabases(databaseCollection)
            return None

    # Reaching this point means that there is no asset database with the URL #url mounted.
    raise RuntimeError(
        f"An asset database with the URL '{url}' cannot be unmounted because it does not exist.")


def AccessUserDatabases():
    """Accesses the data structures representing the user asset databases.

    The accessed AssetDatabaseStruct instances only contain meta information about the user
    databases, not the content of these databases. See AccessImportantRepositories for how to access
    the repositories of the application databases.
    """
    # Wait for all asset databases to be loaded and abort when this is not possible.
    if not maxon.AssetDataBasesInterface.WaitForDatabaseLoading():
        return RuntimeError("Could not load asset databases.")

    # Iterate over all AssetDatabaseStruct instances for the user databases. This will not yield
    # databases provided by the application, but only the databases mounted by the user. A
    # AssetDatabaseStruct instance is also only a surrogate which represents a database and contains
    # no data besides the four fields describing the represented database.
    for database in maxon.AssetDataBasesInterface.GetDatabases():
        print(f"url: {database._dbUrl}, active: {database._active}, " +
              f"builtin: {database._isBuiltin}, is_persistent: {database._exportOnSaveProject}")


def GetImportantRepositories(doc: c4d.documents.BaseDocument):
    """Accesses the builtin, application, user preferences and active document repositories.

    The user preferences repository plays a central role as it contains most of the content which is
    accessible with the Asset Browser and therefor is the usual choice for searching for assets or
    adding assets when there is no dedicated user database repository available.
    """
    if not isinstance(doc, c4d.documents.BaseDocument):
        raise TypeError(f"Expected {c4d.documents.BaseDocument} for 'doc'. Received: {doc}")

    importantRepositories = []

    # The non-writable application repository based on the built-in repository of Cinema 4D, it
    # will contain atomic assets as the application provided node templates.
    importantRepositories.append(
        maxon.AssetInterface.GetApplicationRepository())

    # The writable user preferences repository, it contains the application repository, the asset
    # database shipped with Cinema 4D and the user databases attached to the running instance.
    importantRepositories.append(maxon.AssetInterface.GetUserPrefsRepository())

    # The repository that is associated with the active document, passing #True to will cause a
    # repository to be created when it has not been created yet.
    importantRepositories.append(doc.GetSceneRepository(True))

    # Get the default language of Cinema 4D (en-US) for retrieving the repository names.
    defaultLanguage = maxon.Resource.GetDefaultLanguage()

    for repository in importantRepositories:
        if not repository:
            raise RuntimeError("Repository access did fail.")

        repoId = repository.GetId()
        isWriteable = repository.IsWritable()
        name = repository.GetRepositoryName(defaultLanguage)

        print(f"{repository} ({name}): id - {repoId}, writeable: {isWriteable}")


def CreateRepositories():
    """Creates repositories for all user databases.

    Doing this is usually not necessary for performing light- to medium-sized asset operations, and
    the user preferences repository can then be used instead. Only when there is a substantial
    amount of assets that must be processed, a repository should be constructed to limit the
    search space for search operations. The method CreateRepositoryFromUrl() used in this example
    can also be used to create a repository and its underlying database from scratch when the
    provided URL points to location where no database has been established yet.
    """
    # Wait for all asset databases to be loaded, abort when this is not possible.
    if not maxon.AssetDataBasesInterface.WaitForDatabaseLoading():
        return RuntimeError("Could not load asset databases.")

    # Get the default language of Cinema 4D (en-US) for retrieving the repository names.
    defaultLanguage = maxon.Resource.GetDefaultLanguage()

    # Iterate over all currently mounted databases and create an asset repository for each of them.
    # Doing this is usually not necessary as user asset databases are automatically part of the
    # the user preferences repository which is easier to retrieve. Creating a repository for a
    # specific user asset database can be useful to speed up asset searches.
    for database in maxon.AssetDataBasesInterface.GetDatabases():

        # Create a unique identifier for the repository.
        rid = maxon.AssetInterface.MakeUuid(str(database._dbUrl), True)

        # Repositories can be composed out of other repositories which are called bases. In this
        # case no bases are used to construct the repository. But with bases a repository for all
        # user databases could be constructed for example.
        bases = maxon.BaseArray(maxon.AssetRepositoryRef)

        # Create a writable and persistent repository for the database URL. If #_dbUrl would point
        # to a location where no database has been yet stored, the necessary data would be created.
        repository = maxon.AssetInterface.CreateRepositoryFromUrl(
            rid, bases, database._dbUrl, True, False, False)
        if not repository:
            raise RuntimeError("Repository construction failed.")

        # Access some properties of the newly created repository.
        repoId = repository.GetId()
        isWriteable = repository.IsWritable()
        name = repository.GetRepositoryName(defaultLanguage)

        print(f"{repository} ({name}): id - {repoId}, writeable: {isWriteable}")


def StoreAsset():
    """Stores an asset instance in a repository.

    Assets can be stored in a repository with the method AssetRepositoryInterface::StoreAsset(). But
    this form of creating and storing assets is usually only required for minor asset types as
    keywords, categories and custom third party asset types. The core asset types for scenes,
    materials, objects, nodes, and image and movie files have convenience functions which simplify
    the process of creating assets of that type and StoreAsset is not required in these cases.
    """
    # Get the user preferences repository as the repository to store the new asset in.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    # Instantiate a new category asset and create an asset id for it.
    categoryAsset = maxon.CategoryAsset().Create()
    categoryId = maxon.AssetInterface.MakeUuid("category", False)

    # Store the asset. This raises an error when the operations fails. Against our classic API
    # Python instincts, we do not have to check here if the operation was successful in the maxon
    # API. When some special error handling is required, a try/except/else/finally block must be
    # used. See EraseAsset() for an example.
    assetDescription = repository.StoreAsset(categoryId, categoryAsset)

    # Get the language Cinema 4D is currently running in.
    language = maxon.Resource.GetCurrentLanguage()

    # Set the name of the newly created asset, i.e., the name of the category.
    assetDescription.StoreMetaString(
        maxon.OBJECT.BASE.NAME, "Python SDK Example Category", language)

    # Reveal the newly created asset in the Asset Browser.
    ShowAssetInBrowser(assetDescription)


def CopyAsset():
    """Copies an asset in a repository to another asset.

    Running this example requires an internet connection to access the asset library shipped with
    Cinema 4D (unless the "Cable - USB" asset has already been cached).
    """
    # The id of the asset to copy, the "Cable - USB" asset delivered with the builtin asset library
    # of Cinema 4D.
    sourceId = maxon.Id("file_d0a26639c950371a")

    # Get the asset description for that asset.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    sourceDescription = repository.FindLatestAsset(
        maxon.AssetTypes.File(), sourceId, maxon.Id(), maxon.ASSET_FIND_MODE.LATEST)
    if not sourceDescription:
        raise RuntimeError("Could not find an asset with the id {sourceId}")

    # Create an asset id for the the new copied asset, the prefix "file" is chosen because the
    # "Cable - USB" asset is represented by a FileAsset (of subtype object) and so will be its
    # copy. But that prefix is not required, it is just a non-binding convention, and passing for
    # example "Hello World!" for the prefix would work just fine.
    copyId = maxon.AssetInterface.MakeUuid("file", False)

    # Make a copy of the source asset with the new asset id #copyId. This raises an error when the
    # operations fails. Against our classic API Python instincts, we do not have to check here if
    # the operation was successful in the maxon API. When some special error handling is required,
    # a try/except/else/finally block must be used. See EraseAsset() for an example.
    copyDescription = repository.CopyAsset(copyId, sourceDescription)

    # Get the language Cinema 4D is currently running in.
    language = maxon.Resource.GetCurrentLanguage()

    # Get the string with which the asset is labelled in the Asset Browser.
    assetName = copyDescription.GetMetaString(
        maxon.OBJECT.BASE.NAME, language, "Default Asset Name")

    # Overwrite that name to indicate that it is a copy from the original asset, as the asset
    # name has been copied alongside all other asset metadata when the asset was copied (the primary
    # data of the asset, the actual content, was copied too).
    copyDescription.StoreMetaString(
        maxon.OBJECT.BASE.NAME, f"{assetName} (Python SDK Copy)", language)

    # Reveal the newly copied asset in the Asset Browser.
    ShowAssetInBrowser(copyDescription)


def EraseAsset():
    """Removes an asset from an asset repository permanently.
    """
    # The id of the asset to erase. This must be the id of a user created asset, as assets shipped
    # with Cinema 4D are all read only and cannot be erased. The id given below will therefor not
    # exist in your Cinema 4D instance, and you must replace it with the id of an asset which
    # you did create manually, e.g., with the CopyAsset() example above. The id of an asset can
    # be accessed with the #-button in the "Info-Area" of the Asset Browser.
    eraseId = maxon.Id("file@141571f1463f4129b3c20014468d1f90")

    # Get the asset description for that asset.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    assetDescription = repository.FindLatestAsset(
        maxon.AssetTypes.File(), eraseId, maxon.Id(), maxon.ASSET_FIND_MODE.LATEST)
    if not assetDescription:
        raise RuntimeError("Could not find an asset with the id {eraseId}")

    # Erase the asset. This raises an error when the asset is not contained in #repository.
    try:
        repository.EraseAsset(assetDescription)
    except Exception as error:
        print(f"Erasing the asset '{assetDescription}' failed. ({error})")
    else:
        print(f"Successfully erased {assetDescription} from {repository}")


def SimpleAssetSearch():
    """Performs a simple search operation for assets by their type, id or version.
    """
    # Get the user preferences repository as a repository to search in. This repository is the
    # natural choice for search operations, as it will contain (almost) all other repositories as
    # bases. Other repositories are usually only used when performance is critical (and one wants to
    # search only in a subset of all assets) or the special case of repositories bound to documents.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    # In a simple asset search, the search can be narrowed down by the asset type, id and version.
    # Passing in the empty id for any of these qualifiers will broaden the search in that respect.
    # I.e., passing in the empty id for the type will return any asset type, passing in the empty
    # id for the identifier will return assets with any identifier, and passing in the empty id for
    # the version will return assets of any version.

    # So, searching for example with the arguments (type = maxon.Id(), aid=maxon.Id("123"),
    # version=maxon.Id()) will return assets of any type or version that have the asset id "123".
    # And the arguments (type=maxon.AssetTypes.File(), aid=maxon.Id(), version = maxon.Id())
    # will search for file type assets with any asset id and any version, i.e., it will retrieve all
    # file assets. The asset version is also impacted by the ASSET_FIND_MODE as shown below.

    # In a simple search the retrieved assets will be stored directly in a list.
    receiver = []

    # Search for all category assets with any id or version in #repository, but only retrieve
    # the latest version of each asset. I.e., when there is a version 1.0 and 2.0 of an asset, only
    # version 2.0 will be returned.
    repository.FindAssets(maxon.AssetTypes.Category().GetId(), maxon.Id(), maxon.Id(),
                          maxon.ASSET_FIND_MODE.LATEST, receiver)

    # Iterate over the first five results.
    for assetDescription in receiver[:5 if len(receiver) >= 5 else len(receiver)]:
        print(assetDescription)

    # In the Python API, a special variant is supported by FindAssets() where no #receiver is
    # required and the found assets are being returned directly by the method. The call is otherwise
    # semantically identical to the previous call.
    results = repository.FindAssets(maxon.AssetTypes.Category().GetId(), maxon.Id(), maxon.Id(),
                                    maxon.ASSET_FIND_MODE.LATEST)

    # When searching for a singular asset with a single id, one can also use FindLatestAsset() to
    # directly return the AssetDescription.

    # The id of the "Cable - USB" asset delivered with the builtin asset library of Cinema 4D.
    assetId = maxon.Id("file_d0a26639c950371a")

    assetDescription = repository.FindLatestAsset(
        maxon.AssetTypes.File(), assetId, maxon.Id(), maxon.ASSET_FIND_MODE.LATEST)
    if not assetDescription:
        raise RuntimeError("Could not find an asset with the id {eraseId}")

    print(f"The asset description for the 'Cable - USB' asset: {assetDescription}")


def AdvancedAssetSearch():
    """Performs an advanced search evaluating the metadata of the searched assets.

    Complex asset search operations pass in a callback function for the value receiver of the search
    operation, allowing to filter the assets by their metadata while searching.
    """
    # Get the user preferences repository as a repository to search in. This repository is the
    # natural choice for search operations, as it will contain (almost) all other repositories as
    # bases. Other repositories are usually only used when performance is critical (and one wants to
    # search only in a subset of all assets) or the special case of repositories bound to documents.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    # The dictionary #callbackData is used to store assets found by the callback function
    # MyCallback(). The function has access to this variable because an inner function has access
    # to the objects assigned to variables of an outer function. But an inner function cannot assign
    # a new object (id) to a variable of an outer function. Making all operations which change the
    # object of an outer variable illegal, e.g., =, -=, +=, *=, etc.
    #
    # If you do not understand this restriction, always wrap your data in a mutable object (e.g., a
    # list, dictionary, or a custom class) to nullify it. This is demonstrated below where the list
    # #results is wrapped in the dictionary #callbackData. See LinkMediaAssets() in asset_types.py
    # for a practical example how this can become relevant.
    callbackData = {
        "results": []
    }

    # A callback function which conforms to the callback function signature of #receiver.
    def MyCallback(assetDescription: maxon.AssetDescription) -> bool:
        """Tests if the passed asset is of subtype object and appends it to #results if so.

        Passed in will be the actual #maxon.AssetDescription for an asset, not a copy of it. Which
        means that changing the metadata of that AssetDescription will reflect directly without the
        need for storing the asset description again. This is demonstrated by renaming assets which
        are named "Python SDK Foo" to "Python SDK Bar" (you will need to provide a file type asset
        with such name for this to work, you can pick any asset that is of type file, e.g., scenes,
        objects, materials, etc.). The restriction to file assets is caused by the call of
        FindAssets() which uses this callback function below.
        """
        # Get the metadata of the asset and the subtype of the asset in the metadata.
        assetMetadata = assetDescription.GetMetaData()
        asssetSubtype = assetMetadata.Get(
            maxon.ASSETMETADATA.SubType, maxon.Id())

        # When the asset is of subtype object, append it to the variable #results which is part
        # of the enclosing scope. This works because inner functions have access to their enclosing
        # scope in Python, e.g., #MyCallback has access to the scope of #AdvancedAssetSearch.
        if (asssetSubtype == maxon.ASSETMETADATA.SubType_ENUM_Object):
            callbackData["results"].append(assetDescription)

        # But the callback does not have to pass the data out, it can also be used to modify the
        # metadata of assets directly (or carry out other actions as loading assets).

        # Rename any file type asset with the name "Python SDK Foo" to "Python SDK Bar".

        # Get the language Cinema 4D is currently running in.
        language = maxon.Resource.GetCurrentLanguage()

        # Get the string with which the asset is labelled in the Asset Browser.
        assetName = assetDescription.GetMetaString(
            maxon.OBJECT.BASE.NAME, language, "Default Asset Name")

        if assetName != "Python SDK Foo":
            return True

        # Overwrite the asset name, no further actions are required to make this change apply.
        assetDescription.StoreMetaString(maxon.OBJECT.BASE.NAME, f"Python SDK Bar", language)

        # --- end of inner function scope ----------------------------------------------------------

    # Call FindAssets() with the callback function as the #receiver. The other arguments of
    # #FindAssets still count, causing only file assets with any id or version to be passed to
    # to the callback function.
    didComplete = repository.FindAssets(maxon.AssetTypes.File().GetId(), maxon.Id(), maxon.Id(),
                                        maxon.ASSET_FIND_MODE.LATEST, MyCallback)

    # FindAssets() has a return value even when a receiver is being passed in. When the receiver is
    # a list, that return value will always be #True, as the list cannot cancel a search. But when
    # callback function is being passed, and the function will return #False at any point, then
    # the search will be stopped and #didComplete would be #False, as the search would then have
    # been stopped before all assets have been encountered by the callback.
    print(f"The callback function {MyCallback} has stopped the search early: {not didComplete}")

    # Iterate over the first five object assets attached to #results.
    results = callbackData["results"]
    for assetDescription in results[0: 5 if len(results) > 5 else len(results)]:
        print(assetDescription)


def SortAssets():
    """Sorts assets by their metadata properties.

    It is often required to sort assets by their metadata properties to display them for example
    in a GUI. Unlike in the C++ API, it is not trivial to implement a collection type for
    AssetDescription instances in Python which automatically sorts its entries. Instead,
    #sorted() or list.sort() in conjunction with a key callback must be used.
    """
    # Get user repository and retrieve all the latest keyword assets in it.
    repository = maxon.AssetInterface.GetUserPrefsRepository()
    if not repository:
        raise RuntimeError("Could not access the user preferences repository.")

    receiver = []
    repository.FindAssets(maxon.AssetTypes.Keyword().GetId(), maxon.Id(), maxon.Id(),
                          maxon.ASSET_FIND_MODE.ALL, receiver)

    # The callback function to sort assets.
    def GetNameVersionString(assetDescription: maxon.AssetDescription):
        """Returns the name and version of an asset description as a string.

        Sorting callback functions in Python are odd as in that they do not get passed in
        two values to compare, but one value and then return a string which is sorted
        alphanumerically externally. For sorting asset descriptions a concatenation of the
        relevant metadata attributes must therefor be returned in the order in which the
        assets should be sorted.
        """
        assetName = assetDescription.GetMetaString(
            maxon.OBJECT.BASE.NAME, maxon.Resource.GetCurrentLanguage(), "")
        assetVersion = assetDescription.GetVersion()

        return f"{assetName}{assetVersion}"

    # Sort the results
    receiver.sort(key=GetNameVersionString)

    # Iterate over the first fifty entries.
    for assetDescription in receiver[: 50 if len(receiver) >= 50 else len(receiver)]:
        # Get the asset name and version and print it to the console.
        typeId = assetDescription.GetTypeId()
        assetName = assetDescription.GetMetaString(
            maxon.OBJECT.BASE.NAME, maxon.Resource.GetCurrentLanguage(), "")
        assetVersion = assetDescription.GetVersion()

        print(f"{typeId}: {assetName}({assetVersion})")


if __name__ == "__main__":
    # MountAssetDatabase()
    # UnmountAssetDatabase()
    # AccessUserDatabases()
    # GetImportantRepositories(doc)
    # CreateRepositories()
    # StoreAsset()
    # CopyAsset()
    # EraseAsset()
    # SimpleAssetSearch()
    # AdvancedAssetSearch()
    # SortAssets()
    c4d.EventAdd()