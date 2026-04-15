"""Demonstrates a tool finalization workflow at the example of editing SDS weights.

Tool finalization workflow describes the practice of locking onto a snapshot of scene data and then 
letting the user make rolling changes to the scene with viewport feedback. Each change is based on 
the snapshot data, not the data shown in the viewport or scene, so edits do not build on previous
edits but always on the initial data. Unless the user finalizes the changes, e.g., by clicking an 
"Apply" button, changes are not actually applied to the scene, and rolled back to the initial state 
when the user aborts the tool directly or indirectly. This is a common workflow for tools that can 
also be applied to other cases such as modelling.

Open this dialog example by running the command "Py - SDS Weighting Tool (Finalization Logic)" in the 
Commander (Shift + C). The tool tracks the selection of SDS tags in the scene and lets the user 
modify their weights with a spline custom GUI. Editing the spline will always use the base data, 
although we apply and see the final result in the scene. Only when the user clicks the "Apply" 
button, we finalize the changes and update our base data.

This example has for demonstration purposes not been implemented as an explicit ToolData plugin, but
the same principles can be applied 1:1 there too. The pure dialog approach shows that this can also 
be applied to 'tools' which are not formally a tool.

Subjects:
    - Working with a snapshots of scene data for rolling changes, including undo handling.
    - Tracking scene state changes via core messages
"""
__copyright__ = "Copyright 2026, MAXON Computer"
__author__ = "Ferdinand Hoppe"
__date__ = "10/02/2026"
__license__ = "Apache-2.0 license"

import c4d
import typing
import mxutils

# The title of the plugin, used for the command name and the dialog title.
SDS_WEIGHTING_TOOL_TITLE: str = "Py - SDS Weighting Tool (Finalization Logic)"

class SdsWeightingToolDialog(c4d.gui.GeDialog):
    """Realizes the GUI and logic for the SDS weighting tool.
    """
    # The IDs for the different GUI elements, we use in the dialog.
    ID_GRP_MAIN: int                    = 1000
    ID_GRP_BUTTONS: int                 = 1000
    ID_SPL_WEIGHTING_CURVE: int         = 1100
    ID_BTN_APPLY: int                   = 1200
    ID_BTN_RESET: int                   = 1201

    # The settings for the spline custom GUI, we use. We just use the default settings.
    SETTINGS_SPLINE_CUSTOMGUI: c4d.BaseContainer = c4d.BaseContainer()
    # Whether we want to force the finalization logic. When we set this to #True, the user is forced
    # to press the "Apply" button to keep the changes, otherwise they will be lost when changing 
    # the selection, the dialog loosing focus or closing the dialog. When set to #False, changes
    # will stick even without pressing the "Apply" button.
    FORCE_FINALIZATION: bool = True

    def __init__(self):
        """Initializes the dialog.
        """
        # Holds both the currently tracked SDS tags and their base weight data upon which we can
        # fall back to either reset the weights or calculate the new weights based on the original 
        # values. I.e., this is our "snapshot".
        self._weightingData: list[tuple[c4d.BaseTag, dict]] = []
        # The hash of the current selection of tags, so that we can detect changes in the selection.
        # We just store the set of hashes (their GeMarker UUIDs) for all the tags we track.
        self._selectionHash: set[int] = set()
        # Whether the user finalized the current weights, so that we can decide whether to reset the 
        # weights on selection changes or not.
        self._isFinalized: bool = False
        
    def CreateLayout(self) -> bool:
        """Called by Cinema 4D when the GUI of the dialog is being built.

        Returns:
            bool: True if the layout was created successfully, otherwise False.
        """
        self.SetTitle(SDS_WEIGHTING_TOOL_TITLE)
        self.GroupBegin(self.ID_GRP_MAIN, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=1, rows=0)
        self.GroupBorderSpace(5, 5, 5, 5)
        self.GroupSpace(5, 5)
        # The spline gui we use to edit the weights of tags.
        self.AddCustomGui(self.ID_SPL_WEIGHTING_CURVE, c4d.CUSTOMGUI_SPLINE, "Spline", 
                          c4d.BFH_SCALEFIT, 0, 0, self.SETTINGS_SPLINE_CUSTOMGUI)
        self.AddSeparatorH(0)
        # The Apply and Reset buttons we use to finalize or reset the weights.
        self.GroupBegin(self.ID_GRP_BUTTONS, c4d.BFH_SCALEFIT, cols=2, rows=0)
        if self.FORCE_FINALIZATION:
            self.AddButton(self.ID_BTN_APPLY, c4d.BFH_FIT, name="Apply")
        self.AddButton(self.ID_BTN_RESET, c4d.BFH_FIT, name="Reset")
        self.GroupEnd() # end of ID_GRP_BUTTONS
        self.GroupEnd() # end of ID_GRP_MAIN

        return True
    
    def InitValues(self) -> bool:
        """Called by Cinema 4D after the layout has been created.

        Returns:
            bool: True if the initial values were set successfully, otherwise False.
        """
        spline: c4d.SplineData = c4d.SplineData()
        spline.MakeLinearSplineBezier()
        self.Spline = spline

        self.GatherData()

        return True
    
    def AskClose(self) -> bool:
        """Called by Cinema 4D when the user tries to close the dialog.
        """
        # When the user tries to close the dialog, we reset all unfinalized weights.
        self.ResetWhenNotFinalized(invokeEvent=True)
        return False

    def Command(self, mid: int, data: c4d.BaseContainer) -> bool:
        """Called by Cinema 4D when the user clicked a gadget in the dialog.

        Args:
            mid (int): The ID of the gadget that was clicked.
            data (c4d.BaseContainer): The message data for the click event.

        Returns:
            bool: True if the click event was consumed, False otherwise.
        """
        if mid == self.ID_BTN_APPLY:
            self.FinalizeWeights()
        elif mid == self.ID_BTN_RESET:
            self.ResetWeights(resetSpline=True)
        elif mid == self.ID_SPL_WEIGHTING_CURVE:
            self.UpdateWeights()
        else:
            raise NotImplementedError(f"Command with ID {mid} is not implemented.")

        return True
    
    def Message(self, msg: c4d.BaseContainer, result: c4d.BaseContainer) -> any:
        """Called by Cinema 4D when a message is sent to the dialog.

        Args:
            msg (c4d.BaseContainer): The message data for the message event.
            result (c4d.BaseContainer): The message data for the result of the message event.

        Returns:
            any: The result of the message event.
        """
        # When the dialog looses focus, handle finalization, i.e., reset data when it is not finalized.
        if msg.GetId() == c4d.BFM_LOSTFOCUS:
            self.ResetWhenNotFinalized(invokeEvent=True)
        # When we get focus, grab the newest scene data.
        elif msg.GetId() == c4d.BFM_GOTFOCUS:
            self.GatherData()

        return c4d.gui.GeDialog.Message(self, msg, result)
    

    def CoreMessage(self, mid: int, msg: c4d.BaseContainer) -> bool:
        """Called by Cinema 4D when a core message is sent to the dialog.

        Args:
            msgId (int): The ID of the message that was sent.
            data (c4d.BaseContainer): The message data for the message event.
        """
        # We use this here to track scene changes, and then grab data when something changed. 
        # This is a common approach for 'scanning' plugins that need to react to changes in the 
        # scene, e.g., selection changes, and then update their data accordingly. But we have
        # to be careful not to create feedback loops with our own updates, see comments in 
        # GatherData() and UpdateWeights().
        if mid == c4d.EVMSG_CHANGE:
            self.GatherData()
            
        return super().CoreMessage(mid, msg)
    
    # --- Everything below is custom/business logic which is not part of the GeDialog interface.

    # --- Properties -------------------------------------------------------------------------------
    
    @property
    def Spline(self) -> c4d.SplineData | None:
        """Returns the SplineData of the spline custom GUI.
        """
        gui: c4d.gui.SplineCustomGui | None = self.FindCustomGui(
            self.ID_SPL_WEIGHTING_CURVE, c4d.CUSTOMGUI_SPLINE)
        return gui.GetSplineData() if gui is not None else None
    
    @Spline.setter
    def Spline(self, data: c4d.SplineData) -> None:
        """Sets the SplineData of the spline custom GUI.
        """
        gui: c4d.gui.SplineCustomGui | None = self.FindCustomGui(
            self.ID_SPL_WEIGHTING_CURVE, c4d.CUSTOMGUI_SPLINE)
        if gui is not None:
            gui.SetSpline(data)

    # --- Custom Methods ---------------------------------------------------------------------------

    def FLushData(self) -> None:
        """Flushes all currently tracked SDS data.
        """
        self._weightingData = []
        self._selectionHash = set()
        self._isFinalized = False

    def GatherData(self) -> bool:
        """Gathers all SDS weight tags from the current document selection.
        """
        # This tool assumes to always work on the active document.
        doc: c4d.documents.BaseDocument = c4d.documents.GetActiveDocument()

        # When there are SDS tags selected, we use them.
        selectedTags: list[c4d.BaseTag] = []
        selectedObjects: list[c4d.PolygonObject] = []
        for obj in mxutils.IterateTree(doc.GetFirstObject(), True):
            for tag in obj.GetTags():
                if tag.GetType() == c4d.Tsds and tag.GetBit(c4d.BIT_ACTIVE):
                    selectedTags.append(tag)

        # Only update the selection when there are other tags selected than in the previous 
        # selection. We use the hash of the last selection for this, which is basically the set of 
        # the GeMarker UUIDs of the tags we track. This is important to avoid feedback loops with 
        # our own updates caused by EventAdd() calls we make.
        newSelectionHash: set[int] = set([ hash(tag) for tag in selectedTags ])
        if newSelectionHash == self._selectionHash and not self._isFinalized:
            return True
        
        # Deal with the case that the selection changed but the user did not finalize the weights, 
        # so we reset all weights on the old data.
        self.ResetWhenNotFinalized(invokeEvent=False)

        # Build the new data.
        for tag in selectedTags:
            tag.InitFromObject()

        self.FLushData()
        self._selectionHash = newSelectionHash
        self._weightingData = [(tag, tag.GetTagData()) for tag in selectedTags]

        # When any of the tags has no data, we cannot track them properly, so we abort.
        if any(data is None for _, data in self._weightingData):
            self._weightingData = []
            self._selectionHash = set()
            return False

        return True
    
    def UpdateWeights(self, invokeEvent: bool = True, isFinalizePass: bool = False) -> bool:
        """Updates the weight data of the currently tracked SDS tags with the mappings from the
        spline GUI.
        """
        if len(self._weightingData) == 0:
            return False
        
        # We modify the scene, so this function must be called from the main thread. This check is
        # good practice despite our code already being setup to always run from the main thread.
        if not c4d.threading.GeIsMainThreadAndNoDrawThread():
            raise RuntimeError("UpdateWeights must be called from the main thread.")
        
        # Some book keeping so that undo steps work correctly when we finalize changes.
        doc: c4d.documents.BaseDocument | None = None
        if (isFinalizePass):
            # We cannot finalize dangling tags.
            allAlive: bool = all(tag.IsAlive() for tag, _ in self._weightingData)
            if not allAlive:
                self.FLushData()
                self.GatherData()
                return False
            
            # And each tag should belong to a document, as we otherwise cannot properly create 
            # undo steps for them.
            allHaveDocs: bool = all(tag.GetDocument() is not None for tag, _ in self._weightingData)
            if not allHaveDocs:
                self.FLushData()
                self.GatherData()
                return False
            
            # Reset all weights without an update event so that we have a from state from which we
            # can create the undo. The start the undo block.
            self.ResetWeights(resetSpline=False, invokeEvent=False)
            doc = self._weightingData[0][0].GetDocument()
            doc.StartUndo()
            
        # Walk over all tracked tags and update their weights based on the spline mapping. We use the
        # use the base weight data we gathered in GatherData() to calculate the new weights and
        # apply them.
        didUpdate: bool = False
        for tag, baseWeight in self._weightingData:
            # This is a sanity check for our tag data not having become a dangling pointer. There are
            # more elegant ways to deal with this problem, but we just grab new data here.
            if not tag or not tag.IsAlive():
                self.FLushData()
                self.GatherData()
                return False

            # Make a copy of our base data for this tag into which we can write new data.
            weights: dict = baseWeight.copy()

            # Apply the spline mapping to all vertex weights.
            if "pointweight" in weights:
                weights["pointweight"] = [
                    c4d.utils.RangeMap(value, 0.0, 1.0, 0.0, 1.0, True, self.Spline)
                    for value in weights["pointweight"]
                ]
            # Apply the spline mapping to all edge weights.
            if "polyweight" in weights:
                weights["polyweight"] = [
                    {
                        edge_index: c4d.utils.RangeMap(weight, 0.0, 1.0, 0.0, 1.0, True, self.Spline)
                        for edge_index, weight in poly_data.items()
                    }
                    for poly_data in weights["polyweight"]
                ]
            
            # Only update the tag when we actually changed something. When we are in the finalize 
            # pass, we also create an undo step for the tag when we update it.
            if weights != baseWeight:
                if doc is not None and isFinalizePass:
                    doc.AddUndo(c4d.UNDOTYPE_CHANGE, tag)
            
                tag.SetTagData(weights)
                tag.SetDirty(c4d.DIRTYFLAGS_DATA)
                if (obj := tag.GetObject()) is not None:
                    obj.SetDirty(c4d.DIRTYFLAGS_DATA)
                didUpdate = True

        # Close the undo block when we are in the finalize pass.
        if isFinalizePass and doc is not None:
            doc.EndUndo()

        # Enqueue an update of the GUI, so that our changes are reflected in the viewport. This will 
        # trigger an EVMSG_CHANGE message for which we are listening in CoreMessage, we must therefore
        # make sure that we do not trip over own updates (see comments in GatherData()). This is a 
        # common issue with 'updater' plugins: you must distinguish your own updates from external 
        # updates.
        if didUpdate and invokeEvent:
            c4d.EventAdd()

        return didUpdate

    def ResetWeights(self, resetSpline: bool = False, invokeEvent: bool = True) -> bool:
        """Resets the weight data of the currently tracked SDS tags to their original values.
        """
        for tag, baseWeight in self._weightingData:
            if not tag or not tag.IsAlive():
                self.FLushData()
                self.GatherData()
                return False

            tag.SetTagData(baseWeight)
            tag.SetDirty(c4d.DIRTYFLAGS_DATA)
            if tag.GetObject():
                tag.GetObject().SetDirty(c4d.DIRTYFLAGS_DATA)

        if resetSpline:
            spline: c4d.SplineData = c4d.SplineData()
            spline.MakeLinearSplineBezier()
            self.Spline = spline

        if invokeEvent:
            c4d.EventAdd()

        return True

    def ResetWhenNotFinalized(self, invokeEvent: bool) -> None:
        """Resets all weights when the current weights are not finalized and the instance forces
        finalization.
        """
        if self._weightingData and not self._isFinalized and self.FORCE_FINALIZATION:
            self.ResetWeights(resetSpline=True, invokeEvent=invokeEvent)

    def FinalizeWeights(self) -> None:
        """Finalizes the weight data of the currently tracked SDS tags.
        """
        # We mark ourself as finalized and regather data, which will make the changed data become
        # the new ground truth.
        self.UpdateWeights(invokeEvent=False, isFinalizePass=True)
        self._isFinalized = True
        self.GatherData()

class SdsWeightingToolCommand (c4d.plugins.CommandData):
    """Realizes the command for the SDS weighting tool.
    """
    # The dialog hosted by the plugin.
    REF_DIALOG: SdsWeightingToolDialog | None = None

    @property
    def Dialog(self) -> SdsWeightingToolDialog:
        """Returns the class bound dialog instance.
        """
        if self.REF_DIALOG is None:
            self.REF_DIALOG = SdsWeightingToolDialog()

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
    ID_PLUGIN: int = 1067508

    # The name and help text of the plugin.
    STR_NAME: str = SDS_WEIGHTING_TOOL_TITLE
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
    SdsWeightingToolCommand.Register(iconId=c4d.ID_MODELING_EDGESMOOTH_TOOL)
