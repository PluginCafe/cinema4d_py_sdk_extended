"""Demonstrates a tool that has a bidirectional binding to scene data at the example of a 
'Light Manager'.

Changes made to data monitored by the tool are forwarded to the tool, and changes made in the tool
are forward to the scene. This is a very common pattern used in plugins such as "managers", render
engines, and other tools that have to synchronize their internal state with the scene state.

Subjects:
    - Tool finalization workflow with working with a snapshot of scene data and rolling changes
      for edits or when the user aborts the tool, including undo handling.
    - Tracking scene state changes via core messages

Technical Overview:
    This example effectively builds scene metadata with which we can unambiguously identify and
    get scene data. Looking at the final outcome, one might ask why we are all doing this. Why do we 
    not simply store objects and documents in lists? Let us find out together and assume we have this 
    simple scene:

        Scene
        ├─ Cube
        │  ├─ Light_0
        │  └─ Cone
        └─ Sphere
            └─ Light_1

    We now wrote a light lister plugin, which scanned this scene and stored the following data in
    code, where #trackedLights now hold references to #Light_0 and #Light_1:

        trackedLights: list[c4d.BaseObject] = [
            light for light in mxutils.IterateTree(doc.GetFirstObject(), True)
            if light.GetType() == c4d.Olight
        ]

    That should be a safe way to access and track the light objects, right? Well, unfortunately not. 
    Let us assume the user adds a new light and we have a scene update, and our scene now looks like
    this (the effect described below could also happen with no user changes at all):

        Scene
        ├─ Cube
        │  ├─ Light_0
        │  └─ Cone
        └─ Sphere
            ├─ Light_1
            └─ Light_2

    We now run code, to find out if Light_0 is still in the scene. It could look like this:

        for item in mxutils.IterateTree(doc.GetFirstObject(), True):
            if item.GetName() == "Light_0" and item in trackedLights:
                print ("Light_0 is still there.")

    That should print "Light_0 is still there.", right? Well, chances are good that this print 
    statement will not be executed. But why, did we not just put that very light into #trackedLights?
    The reason why this can fail is that the 'Light_0' which Cinema 4D has given us when we built 
    our #trackedLights list might not be the same 'Light_0' which we get when we traverse the scene 
    after the update. 

    They might look and behave identical, but under the hood Cinema 4D might have destroyed the old 
    'Light_0' and created a new one with the same name and properties. When this happens, Cinema 4D 
    (or the user) deallocated something, and we still hold a reference to it, the respective C4DAtom 
    will return #False for IsAlive() and all other calls to that reference will fail with the error 
    message that the object is not alive. So, our list #trackedLights can turn into a list of dead 
    pointers, even when the data is actually still in the scene, just in a new incarnation. This can 
    happen with any scene element, be it a document itself, an object, a tag, a material, render 
    settings, and so on.

        # This might now print #False twice.
        for light in trackedLights:
            print (light.IsAlive())

    This does not mean that we can never store any references to scene data, within the scope of a 
    function that is okay. But we can never use references as long time storage for scene data. 
    Because when we access it, the user or Cinema 4D might have long deleted that data.

    This code example offers the solution to this problem. Internally, Cinema 4D marks each scene 
    element with a marker that uniquely identifies it within the scene. This marker will stay the 
    same, even when Cinema 4D reallocates an element. It will even stay the same over scene saves 
    and reloads. So, if we want to long term track scene elements, we can either use builtin methods 
    such as BaseLink or store these unique markers to identify the elements we want to track. In 
    Python, this data can be accessed via C4DAtom.FindUniqueID() or via C4DAtom.__hash__(). 
    FindUniqueID() returns a memoryview on the unique marker data. While __hash__() returns an int 
    which is a hash of that unique marker data. While the output is different, they both express the 
    same underlying unique marker.

        # Build a list of UUIDs for the found light objects.
        uuids: list[int] = []
        alsoUuids: list[bytes] = []
        for light in mxutils.IterateTree(doc.GetFirstObject(), True):
            if light.GetType() == c4d.Olight:
                uuids.append(hash(light))
                alsoUuids.append(bytes(light.FindUniqueID(c4d.MAXON_CREATOR_ID)))
"""
__copyright__ = "Copyright 2026, MAXON Computer"
__author__ = "Ferdinand Hoppe"
__date__ = "10/02/2026"
__license__ = "Apache-2.0 license"

import c4d
import mxutils
import typing

# The title of the plugin, used for the command name and the dialog title.
LIGHT_TOOL_TITLE: str = "Py - Light Tool (Scene Synchronization Logic)"

class LightToolDialog (c4d.gui.GeDialog):
    """Tracks the existence of light objects and their parameter changes in a scene.
    """
    # Dialog element IDs.
    ID_GRP_MAIN: int = 1000
    ID_GRP_DYN_LIGHTS_CONTAINER: int = 1001
    ID_GRP_DYN_LIGHT_ROW: int = 1002

    ID_CHK_CONSOLE_OUTPUT: int = 2000
    ID_DYN_LIGHT_OFFSET: int = 10000

    # Some minor symbols for managing the internal lookup table.
    NEW_LIGHT: int = 0     # A new light has been found
    UPDATED_LIGHT: int = 1 # An existing light has been updated.

    def __init__(self) -> None:
        """Initializes a LightTrackerDialog and its internal table tracking a scene state.
        """
        # The light types and parameters we track.
        self._trackedTypesAndParameters: dict[int, list[int]] = {
            c4d.Olight: [c4d.LIGHT_TYPE, c4d.LIGHT_BRIGHTNESS, c4d.LIGHT_COLOR],
            c4d.Orslight: [c4d.REDSHIFT_LIGHT_TYPE,
                            c4d.REDSHIFT_LIGHT_PHYSICAL_INTENSITY,
                            c4d.REDSHIFT_LIGHT_PHYSICAL_COLOR],
        }

        self._lightTable: dict[bytes: dict] = {}

        # The internal data of the tool, we track light objects via their hashes (int) and store
        # their data as a dictionary.
        self._data: dict[int, int] = {}
        self._trackedDocument: int | None = None
        self._consoleOutput: bool = True

    def CreateLayout(self) -> bool:
        """Adds GUI gadgets to the dialog.

        Not needed in this case, as we do not want to use GeDialog as a dialog, but for its ability
        to receive core messages.
        """
        self.SetTitle(LIGHT_TOOL_TITLE)
        self.GroupBorderSpace(5, 5, 5, 5)
        self.AddStaticText(id=1000, flags=c4d.BFH_SCALEFIT, inith=25, name='This GUI has no items.')
        return True

    def CoreMessage(self, mid: int, data: c4d.BaseContainer) -> bool:
        """Receives core messages broadcasted by Cinema 4D.
        """
        # Some change has been made to a document.
        if mid == c4d.EVMSG_CHANGE:
            self.ScanActiveScene()
        return 0
    
    def Message(self, msg: c4d.BaseContainer, result: c4d.BaseContainer) -> any:
        """Called by Cinema 4D when a message is sent to the dialog.

        Args:
            msg (c4d.BaseContainer): The message data for the message event.
            result (c4d.BaseContainer): The message data for the result of the message event.

        Returns:
            any: The result of the message event.
        """
        # When we get focus, grab the newest scene data.
        if msg.GetId() == c4d.BFM_GOTFOCUS:
            self.ScanActiveScene()

        return c4d.gui.GeDialog.Message(self, msg, result)
    
    # --- Custom Methods ---------------------------------------------------------------------------

    def ScanActiveScene(self) -> tuple[list[int], list[int]]:
        """Scans the active document for changes in tracked light objects.
        """
        return self.ScanScene(c4d.documents.GetActiveDocument())

    def ScanScene(self, doc: c4d.documents.BaseDocument) -> tuple[list[int], list[int]]:
        """
        """
        # Get all tracked light objects that are of a type we want to track.
        mxutils.CheckType(doc, c4d.documents.BaseDocument)
        allLights: list[c4d.BaseObject] = [
            n for n in mxutils.IterateTree(doc.GetFirstObject(), True)
            if self._trackedTypesAndParameters.get(n.GetType(), None) is not None
        ]
        if not allLights:
            return [], []

        # Store of the hash of the document we are tracking, so that we can later easily verify
        # that a given document X is the same as the one we are tracking by comparing hash(X)
        # to this value. #hash() will call C4DAtom.__hash__(), which in turn will hash the 
        # MAXON_CREATOR_ID unique ID of the element.
        self._trackedDocument = hash(doc)

        # Build a list of UUIDs for the found light objects, so that we can compare them with our 
        # stored data.
        allUuids: list[int] = [hash(n) for n in allLights]

        # Now build a list of all new lights, by checking if the UUIDs are already in the internal 
        # table. And the list of changed lights, by checking if the DIRTYFLAGS_DATA checksum of the 
        # object is higher than the cached value in the internal table.
        newLights: list[int] = [u for u in allUuids if u not in self._data.keys()]
        changedLights: list[int] = [u for u, l in zip(allUuids, allLights) 
                                    if self._data.get(u, c4d.NOTOK) != l.GetDirty(c4d.DIRTYFLAGS_DATA)]

        # Finally, update the internal table with new dirty data.
        for light in allLights:
            uuid: int = hash(light)
            self._data[uuid] = light.GetDirty(c4d.DIRTYFLAGS_DATA)

        # Print out the changes when console output is enabled.
        if self._consoleOutput:
            if len(newLights) < 1:
                print ("No lights have been added.")
            else:
                print ("The following new lights have been found:")
                for uuid in newLights:
                    light: c4d.BaseObject = allLights[allUuids.index(uuid)]
                    print(f"\tuuid: {uuid}: name: {light.GetName()}")

            if len(changedLights) < 1:
                print ("No lights have been modified.")
            else:
                print ("The following lights have been modified:")
                for uuid in changedLights:
                    light: c4d.BaseObject = allLights[allUuids.index(uuid)]
                    print(f"\tuuid: {uuid}: name: {light.GetName()}")

        return newLights, changedLights
    
    def GetLight(self, sceneUuid: int, lightUuid: int) -> c4d.BaseObject | None:
        """Returns the light object for a given uuid in a given scene.
        """
        # Just as for the builtin BaseLink system (which works with the same basic mechanism), an
        # uuid is worthless without the context of a scene, as it only identifies an element within 
        # a given scene.

        # We can fashion this function be getting passed a document, but for demonstration purposes,
        # we use an document UUID. While the rest of the plugin does not actively supports this, as
        # the data will be updated as soon as the scene changes, this function as is would work
        # over active scene boundaries. In an extreme case, one could even start loading scenes
        # from disk, to attempt to find a scene with the given #sceneUuid, we 'just' iterate over 
        # all open documents and check their UUIDs until we find a match.
        doc: c4d.documents.BaseDocument = c4d.documents.GetFirstDocument()
        foundScene: bool = False
        while doc and not foundScene:
            if hash(doc) == sceneUuid:
                foundScene = True
            else:
                doc = doc.GetNext()

        if not foundScene:
            print (f"Could not find a scene with the given uuid {sceneUuid}.")
            return None
        
        # Now we have the document, we can iterate over the scene to find the light with the given uuid.
        light: c4d.BaseObject | None = None
        for obj in mxutils.IterateTree(doc.GetFirstObject(), True):
            if hash(obj) == lightUuid:
                return obj
            
        print (f"Could not find a light with the given uuid {lightUuid} in the scene with uuid {sceneUuid}.")
        return None


class LightToolCommand (c4d.plugins.CommandData):
    """Realizes the command for the light tool dialog.
    """
    # The dialog hosted by the plugin.
    REF_DIALOG: LightToolDialog | None = None

    @property
    def Dialog(self) -> LightToolDialog:
        """Returns the class bound dialog instance.
        """
        if self.REF_DIALOG is None:
            self.REF_DIALOG = LightToolDialog()

        return self.REF_DIALOG

    def Execute(self, doc: c4d.documents.BaseDocument) -> bool:
        """Folds or unfolds the dialog.
        """
        if self.Dialog.IsOpen() and not self.Dialog.GetFolding():
            self.Dialog.SetFolding(True)
        else:
            self.Dialog.Open(c4d.DLG_TYPE_ASYNC, self.ID_PLUGIN, defaultw=300, defaulth=300)

        return True

    def RestoreLayout(self, secret: any) -> bool:
        """Restores the dialog on layout changes.
        """
        return self.Dialog.Restore(self.ID_PLUGIN, secret)

    def GetState(self, doc: c4d.documents.BaseDocument) -> int:
        """Sets the command icon state of the plugin.
        """
        result: int = c4d.CMD_ENABLED
        if self.Dialog.IsOpen() and not self.Dialog.GetFolding():
            result |= c4d.CMD_VALUE

        return result
    
    # The unique ID of the plugin, it must be obtained from developers.maxon.net.
    ID_PLUGIN: int = 1067514

    # The name and help text of the plugin.
    STR_NAME: str = LIGHT_TOOL_TITLE
    STR_HELP: str = ("Opens a dialog to make rolling changes to the selected SDS tags, based on a" 
                     "a spline GUI, which can then be finalized or discarded.")

    @classmethod
    def Register(cls: typing.Type, iconId: int) -> None:
        """Registers the command plugin.

        This is a custom method and not part of the CommandData interface.
        """
        bitmap: c4d.bitmaps.BaseBitmap = c4d.bitmaps.InitResourceBitmap(iconId)
        c4d.plugins.RegisterCommandPlugin(
            id=cls.ID_PLUGIN, str=cls.STR_NAME, info=0, icon=bitmap, help=cls.STR_HELP, dat=cls())


# Called by Cinema 4D when this plugin module is loaded.
if __name__ == '__main__':
    LightToolCommand.Register(iconId=c4d.ID_MODELING_EDGESMOOTH_TOOL)
