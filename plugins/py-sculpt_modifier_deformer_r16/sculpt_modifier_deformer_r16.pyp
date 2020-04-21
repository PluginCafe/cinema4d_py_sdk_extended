"""
Copyright: MAXON Computer GmbH
Author: Kent Barber

Description:
    - Modifier, modifying a point object using the pull sculpting brush tool.

Class/method highlighted:
    - c4d.plugins.ObjectData
    - ObjectData.Init()
    - ObjectData.Message()
    - ObjectData.ModifyObject()
    - c4d.modules.sculpting.SculptModifierInterface
    - SculptModifierInterface.Init()
    - SculptModifierInterface.GetDefaultData()
    - SculptModifierInterface.SetData()
    - SculptModifierInterface.SetData()
    - SculptModifierInterface.ApplyModifier()

Compatible:
    - Win / Mac
    - R16, R17, R18, R19, R20, R21
"""
import c4d
import random

# be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1031586 
ID_SCULPT_BRUSH_PULL_MODIFIER = 1030505


class SculptModifierDeformer(c4d.plugins.ObjectData):

    def __init__(self):
        self.brushInterface = None

    def Init(self, node):
        """
        Called when Cinema 4D Initialize the ObjectData (used to define, default values)
        :param node: The instance of the ObjectData.
        :type node: c4d.GeListNode
        :return: True on success, otherwise False.
        """
        self.InitAttr(node, float, c4d.PYSCULPTMODIFIERDEFORMER_RADIUS)
        self.InitAttr(node, float, c4d.PYSCULPTMODIFIERDEFORMER_PRESSURE)
        self.InitAttr(node, bool, c4d.PYSCULPTMODIFIERDEFORMER_STAMP_ACTIVE)
        self.InitAttr(node, int, c4d.PYSCULPTMODIFIERDEFORMER_NUMSTAMPS)
        self.InitAttr(node, bool, c4d.PYSCULPTMODIFIERDEFORMER_STAMP_USEFALLOFF)
        self.InitAttr(node, int, c4d.PYSCULPTMODIFIERDEFORMER_SEED)
        self.InitAttr(node, float, c4d.PYSCULPTMODIFIERDEFORMER_STAMP_ROTATION)

        node[c4d.PYSCULPTMODIFIERDEFORMER_RADIUS] = 20
        node[c4d.PYSCULPTMODIFIERDEFORMER_PRESSURE] = 0.2
        node[c4d.PYSCULPTMODIFIERDEFORMER_STAMP_ACTIVE] = False
        node[c4d.PYSCULPTMODIFIERDEFORMER_NUMSTAMPS] = 10
        node[c4d.PYSCULPTMODIFIERDEFORMER_STAMP_USEFALLOFF] = True
        node[c4d.PYSCULPTMODIFIERDEFORMER_SEED] = 0
        node[c4d.PYSCULPTMODIFIERDEFORMER_STAMP_ROTATION] = 0

        self.brushInterface = c4d.modules.sculpting.SculptModifierInterface()

        return True

    def Message(self, node, msgId, data):
        """
        Called by Cinema 4D part to notify the object to a special event
        :param node: The instance of the ObjectData.
        :type node: c4d.BaseObject
        :param msgId: The message ID type.
        :type msgId: int
        :param data: The message data.
        :type data: Any, depends of the message passed.
        :return: Depends of the message type, most of the time True.
        """
        # MSG_MENUPREPARE is received when called from the menu, to let some setup work.
        # In the case of this message, the data passed is the BaseDocument the object is inserted
        if msgId == c4d.MSG_MENUPREPARE:
            # Enables the modifier
            node.SetDeformMode(True)
        return True

    def ModifyObject(self, mod, doc, op, op_mg, mod_mg, lod, flags, thread):
        """
        Called by Cinema 4D with the object to modify.
        :param mod: The Python Modifier.
        :type mod: c4d.BaseObject
        :param doc: The document containing the plugin object.
        :type doc: c4d.documents.BaseDocument
        :param op: The object to modify.
        :type op: c4d.BaseObject
        :param op_mg: The object's world matrix.
        :type op_mg: c4d.Matrix
        :param mod_mg: The modifier object's world matrix.
        :type mod_mg: c4d.Matrix
        :param lod: The level of detail.
        :type lod: float
        :param flags: Currently unused.
        :type flags: int
        :param thread: The calling thread.
        :type thread: c4d.threading.BaseThread
        :return: True if the object was modified, otherwise False.
        """
        # Retrieves object parameters values
        data = mod.GetDataInstance()
        radius = data[c4d.PYSCULPTMODIFIERDEFORMER_RADIUS]
        pressure = data[c4d.PYSCULPTMODIFIERDEFORMER_PRESSURE] * 100.0
        stampActive = data[c4d.PYSCULPTMODIFIERDEFORMER_STAMP_ACTIVE]
        stampTexture = data[c4d.PYSCULPTMODIFIERDEFORMER_STAMP_TEXTURE]
        numStamps = data[c4d.PYSCULPTMODIFIERDEFORMER_NUMSTAMPS]
        useFalloff = data[c4d.PYSCULPTMODIFIERDEFORMER_STAMP_USEFALLOFF]
        seed = data[c4d.PYSCULPTMODIFIERDEFORMER_SEED]
        rotation = data[c4d.PYSCULPTMODIFIERDEFORMER_STAMP_ROTATION]

        # Checks if the passed object is not a polygon object (so its only modify polygon object)
        if not op.CheckType(c4d.Opolygon):
            return True

        # Initializes the brushInterface with the Polygon object passed
        if not self.brushInterface.Init(op):
            return True

        # Retrieves the settings for the brush
        brushData = self.brushInterface.GetDefaultData()

        # Defines settings according our needs
        modifierData = c4d.BaseContainer()
        brushData.SetFloat(c4d.MDATA_SCULPTBRUSH_SETTINGS_STRENGTH, pressure)
        brushData.SetFloat(c4d.MDATA_SCULPTBRUSH_SETTINGS_RADIUS, radius)
        brushData.SetBool(c4d.MDATA_SCULPTBRUSH_STAMP, stampActive)
        brushData.SetFilename(c4d.MDATA_SCULPTBRUSH_STAMP_TEXTUREFILENAME, stampTexture)
        brushData.SetBool(c4d.MDATA_SCULPTBRUSH_STAMP_USEFALLOFF, useFalloff)
        brushData.SetFloat(c4d.MDATA_SCULPTBRUSH_STAMP_ROTATION_VALUE, rotation)

        # Push back our settings to the brush
        self.brushInterface.SetData(brushData, modifierData)

        # Defines the random seed, so random is consistent over time
        random.seed(seed)

        for i in range(numStamps):
            # Retrieves a random a pointIndex
            ptId = int(random.random() * op.GetPointCount())

            # Applies the modification (like if the user click use the brush tool),
            # this will modify the object brushInterface is initialized with.
            self.brushInterface.ApplyModifier(ID_SCULPT_BRUSH_PULL_MODIFIER, ptId, brushData, modifierData)

        # Notifies the object, that internal data changed and it needs to be updated
        op.Message(c4d.MSG_UPDATE)

        return True


if __name__ == "__main__":
    # Registers the object plugin
    c4d.plugins.RegisterObjectPlugin(id=PLUGIN_ID,
                                     str="Py-SculptModifierDeformer",
                                     g=SculptModifierDeformer,
                                     description="opysculptmodifierdeformer",
                                     icon=None,
                                     info=c4d.OBJECT_MODIFIER)
