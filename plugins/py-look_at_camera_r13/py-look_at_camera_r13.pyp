"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam

Description:
    - Tag, force the host object to look at the camera (like the Look At Camera Tag).

Class/method highlighted:
    - c4d.plugins.ObjectData
    - NodeData.Init()
    - TagData.Execute()
"""
import os
import c4d

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1028284


class LookAtCamera(c4d.plugins.TagData):
    """Look at Camera"""
    
    def Init(self, node, isCloneInit=False):
        """Called when Cinema 4D Initialize the TagData (used to define, default values).

        Args:
            node (c4d.GeListNode): The instance of the TagData.
            isCloneInit (bool): True if the tag data is a copy of another one.

        Returns:
            True on success, otherwise False.
        """
        self.InitAttr(node, bool, c4d.PYLOOKATCAMERA_PITCH)
        node[c4d.PYLOOKATCAMERA_PITCH] = True

        pd = c4d.PriorityData()
        if pd is None:
            raise MemoryError("Failed to create a priority data.")

        pd.SetPriorityValue(c4d.PRIORITYVALUE_CAMERADEPENDENT, True)
        node[c4d.EXPRESSION_PRIORITY] = pd

        return True
    
    def Execute(self, tag, doc, op, bt, priority, flags):
        """Called by Cinema 4D at each Scene Execution, this is the place where calculation should take place.

        Args:
            tag (c4d.BaseTag): The instance of the TagData.
            doc (c4d.documents.BaseDocument): The host document of the tag's object.
            op (c4d.BaseObject): The host object of the tag.
            bt (c4d.threading.BaseThread): The Thread that execute the this TagData.
            priority (EXECUTIONPRIORITY): Information about the execution priority of this TagData.
            flags (EXECUTIONFLAGS): Information about when this TagData is executed.
        """
        # Retrieves the current active base draw
        bd = doc.GetRenderBaseDraw()
        if bd is None:
            return c4d.EXECUTIONRESULT_OK

        # Retrieves the active camera
        cp = bd.GetSceneCamera(doc) if bd.GetSceneCamera(doc) is not None else bd.GetEditorCamera()
        if cp is None:
            return c4d.EXECUTIONRESULT_OK

        # Calculates the position to target
        local = cp.GetMg().off * (~(op.GetUpMg() * op.GetFrozenMln())) - op.GetRelPos()

        # Calculates the rotation to target
        hpb = c4d.utils.VectorToHPB(local)

        if not tag[c4d.PYLOOKATCAMERA_PITCH]:
            hpb.y = op.GetRelRot().y
        hpb.z = op.GetRelRot().z

        # Defines the rotation
        op.SetRelRot(hpb)
        
        return c4d.EXECUTIONRESULT_OK


if __name__ == "__main__":
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "tpylookatcamera.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    c4d.plugins.RegisterTagPlugin(id=PLUGIN_ID,
                                  str="Py - LookAtCamera",
                                  info=c4d.TAG_EXPRESSION | c4d.TAG_VISIBLE,
                                  g=LookAtCamera,
                                  description="Tpylookatcamera",
                                  icon=bmp)
