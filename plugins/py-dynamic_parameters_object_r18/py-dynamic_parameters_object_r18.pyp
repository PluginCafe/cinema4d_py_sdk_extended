"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam

Description:
    - Generator, which handle dynamics descriptions and link the parameter angle of first phong tag from the generator.

Class/method highlighted:
    - c4d.plugins.ObjectData
    - NodeData.Init()
    - NodeData.CopyTo()
    - NodeData.Read()
    - NodeData.Write()
    - NodeData.GetDDescription()
    - NodeData.SetDParameter()
    - NodeData.GetDParameter()
    - NodeData.TranslateDescID()
    - NodeData.GetDEnabling()
    - NodeData.GetBubbleHelp()
"""
import copy
import random
import c4d

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1037871

# Dynamic group and parameters IDs
OPYDYNAMICPARAMETERSOBJECT_DYNAMICGROUP = 1100
OPYDYNAMICPARAMETERSOBJECT_DYNAMICGROUP_FIRSTPARAMETER = OPYDYNAMICPARAMETERSOBJECT_DYNAMICGROUP + 1

# Dynamic Object plugin Example for the Dynamic Description additions in R18 Python API
# Parameter ID 1001: REAL parameter OPYDYNAMICPARAMETERSOBJECT_TRANSLATED_PHONG_ANGLE (refers the first attached Phong tag PHONGTAG_PHONG_ANGLE parameter, see TranslateDescID() below)
# Parameter ID 1002: LONG parameter OPYDYNAMICPARAMETERSOBJECT_PARAMETERSNUMBER for the number of parameters in the dynamic group
# Parameter ID 1000: Dynamic Group
# Parameters ID 1100+: Dynamic float parameters


class DynamicParametersObjectData(c4d.plugins.ObjectData):

    def __init__(self):
        self.parameters = []    # Dynamic parameters value
        self.randomID = 0       # Random dynamic parameter ID to disable (see GetDEnabling() below)

    def Init(self, node):
        """Called by Cinema 4D on the initialization of the ObjectData, usually the place to define parameters value.

        Args:
            node (c4d.GeListNode): The instance of the ObjectData.

        Returns:
            bool: True if the initialization was successful, otherwise False, preventing Cinema 4D from creating the object.
        """

        # Defines how many parameters the object will have
        node[c4d.OPYDYNAMICPARAMETERSOBJECT_PARAMETERSNUMBER] = 10

        return True

    def Message(self, node, msgId, data):
        """Called by Cinema 4D to notify the object of a event.

        Args:
            node (c4d.BaseObject): The instance of the ObjectData.
            msgId (int): The message ID type.
            data (Any): The message data, the type depends on the message type.

        Returns:
            Any: Depends of the message type, most of the time True.
        """
        # MSG_MENUPREPARE is received when called from the menu, to let some setup work.
        # In the case of this message, the data passed is the BaseDocument the object is inserted
        if msgId == c4d.MSG_MENUPREPARE:
            # Creates a Phong Tag
            pTag = c4d.BaseTag(c4d.Tphong)
            if pTag is None:
                raise MemoryError("Failed to create a phong tag.")

            # Inserts the tag on the object
            node.InsertTag(pTag)
        return True

    def CopyTo(self, dest, snode, dnode, flags, trn):
        """Called by Cinema 4D when the current object instance is copied.

        The purpose is to copy the member variable from source variable to destination variable.

        Args:
            dest (c4d.plugins.NodeData): The new instance of the ObjectData where the data need to be copied.
            snode (c4d.GeListNode): The source node data, i.e. the current node.
            dnode (c4d.GeListNode): The new node data where the data need to be copied.
            flags (COPYFLAGS): The copy flags.
            trn (c4d.AliasTrans): An alias translator for the operation.

        Returns:
            True if the data was copied successfully, otherwise False.
        """
        # Copies dynamic parameters value to the destination instance of ObjectData
        dest.parameters = copy.copy(self.parameters)

        return True

    def Read(self, node, hf, level):
        """Called by Cinema 4D, when a file with an instance the ObjectData is opened.

        The purpose is to read the data you stored in the Write method to restore your object parameter state.

        Args:
            node (c4d.GeListNode): The instance of the ObjectData.
            hf (c4d.storage.HyperFile): The HyperFile to read from.
            level (int): The plugin version number for your settings.

        Returns:
            bool: True if the data has been read successfully, otherwise False.
        """

        # Reads the number of dynamic parameters
        count = hf.ReadInt32()

        # Reads the dynamic parameters value
        for idx in range(count):
            value = hf.ReadFloat32()
            self.parameters.append(value)

        return True

    def Write(self, node, hf):
        """Called by Cinema 4D, when the document is saved in order to save custom parameters.

        The purpose is to write data and read them back with the Read method.

        Args:
            node (c4d.GeListNode): The instance of the ObjectData.
            hf (c4d.storage.HyperFile): The HyperFile to write into.

        Returns:
            bool: True if the data was written successfully, otherwise False.
        """

        # Writes the number of dynamic parameters
        count = len(self.parameters)
        hf.WriteInt32(count)

        # Writes the dynamic parameters value
        for value in self.parameters:
            hf.WriteFloat32(value)

        return True

    def GetDDescription(self, node, description, flags):
        """Called by Cinema 4D when the description (UI) is queried.

        Args:
            node (c4d.GeListNode): The instance of the ObjectData.
            description (c4d.Description): The description to modify.
            flags: return: The success status or the data to be returned.

        Returns:
            Union[Bool, tuple(bool, Any, DESCFLAGS_DESC)]: The success status or the data to be returned.
        """
        data = node.GetDataInstance()

        # Loads the parameters from the description resource before adding dynamic parameters.
        if not description.LoadDescription(node.GetType()):
            return False

        # Get description single ID
        singleID = description.GetSingleDescID()

        # Declare dynamic group DescID
        dynamicGroupID = c4d.DescID(c4d.DescLevel(OPYDYNAMICPARAMETERSOBJECT_DYNAMICGROUP, c4d.DTYPE_GROUP, node.GetType()))

        # Check if dynamic group needs to be added
        addDynamicGroup = singleID is None
        if not addDynamicGroup:
            addDynamicGroup = dynamicGroupID.IsPartOf(singleID)[0]

        # Adds dynamic group
        if addDynamicGroup:
            bc = c4d.GetCustomDataTypeDefault(c4d.DTYPE_GROUP)
            bc.SetString(c4d.DESC_NAME, "Dynamic Group")
            bc.SetInt32(c4d.DESC_COLUMNS, 1)
            if not description.SetParameter(dynamicGroupID, bc, c4d.DescID(c4d.DescLevel((c4d.ID_OBJECTPROPERTIES)))):
                return False

        # Declare REAL parameter container
        bc = c4d.GetCustomDataTypeDefault(c4d.DTYPE_REAL)
        bc.SetInt32(c4d.DESC_CUSTOMGUI, c4d.CUSTOMGUI_REALSLIDER)
        bc.SetFloat(c4d.DESC_MIN, 0.0)
        bc.SetFloat(c4d.DESC_MAX, 1.0)
        bc.SetFloat(c4d.DESC_MINSLIDER, 0.0)
        bc.SetFloat(c4d.DESC_MAXSLIDER, 1.0)
        bc.SetFloat(c4d.DESC_STEP, 0.01)
        bc.SetInt32(c4d.DESC_UNIT, c4d.DESC_UNIT_FLOAT)
        bc.SetInt32(c4d.DESC_ANIMATE, c4d.DESC_ANIMATE_ON)
        bc.SetBool(c4d.DESC_REMOVEABLE, False)

        # Initialize/Update parameters value list if needed 
        parametersNum = data.GetInt32(c4d.OPYDYNAMICPARAMETERSOBJECT_PARAMETERSNUMBER)
        parametersLen = len(self.parameters)
        if parametersLen == 0:
            self.parameters = [0.0]*parametersNum
        elif parametersLen != parametersNum:
            if parametersLen < parametersNum:
                while parametersLen < parametersNum:
                    self.parameters.append(0.0)
                    parametersLen += 1
            else:
                while parametersLen > parametersNum:
                    self.parameters.pop()
                    parametersLen -= 1

        # Adds dynamic REAL parameters
        for idx in range(parametersNum):
            descid = c4d.DescID(c4d.DescLevel(OPYDYNAMICPARAMETERSOBJECT_DYNAMICGROUP_FIRSTPARAMETER+idx, c4d.DTYPE_REAL, node.GetType()))
            addParameter = singleID is None
            if not addParameter:
                addParameter = descid.IsPartOf(singleID)[0]

            if addParameter:
                name = "Dynamic REAL " + str(idx+1)
                bc.SetString(c4d.DESC_NAME, name)
                bc.SetString(c4d.DESC_SHORT_NAME, name)
                if not description.SetParameter(descid, bc, dynamicGroupID):
                    break

        # Calculate random ID in the dynamic parameters range
        if parametersNum > 1:
            self.randomID = random.randrange(OPYDYNAMICPARAMETERSOBJECT_DYNAMICGROUP_FIRSTPARAMETER, OPYDYNAMICPARAMETERSOBJECT_DYNAMICGROUP_FIRSTPARAMETER + parametersNum - 1)

        # After dynamic parameters have been added successfully, return True and c4d.DESCFLAGS_DESC_LOADED with the input flags
        return True, flags | c4d.DESCFLAGS_DESC_LOADED

    def SetDParameter(self, node, id, data, flags):
        """Called by Cinema 4D, when SetParameter is call from the node. 

        The main purpose is to store the data for member variable. It is necessary for parameters that are not simply stored in the node's container e.g. class members.

        Args:
            node (c4d.GeListNode): The instance of the ObjectData.
            id (c4d.DescID): The parameter Id.
            data (Any): the data, the user defines and we have to store.
            flags (DESCFLAGS_SET): The input flags passed to define the operation.

        Returns:
            Union[Bool, tuple(bool, Any, DESCFLAGS_SET)]: The success status or the data to be returned.
        """
        # Retrieves the parameter ID requested
        paramID = id[0].id

        # Retrieves the parameters count
        parametersLen = len(self.parameters)

        # Checks if passed parameter ID is a dynamic parameter
        if OPYDYNAMICPARAMETERSOBJECT_DYNAMICGROUP_FIRSTPARAMETER <= paramID <= OPYDYNAMICPARAMETERSOBJECT_DYNAMICGROUP+parametersLen:
            # Store the parameter data
            self.parameters[paramID-OPYDYNAMICPARAMETERSOBJECT_DYNAMICGROUP_FIRSTPARAMETER] = data
            return True, flags | c4d.DESCFLAGS_SET_PARAM_SET

        return False

    def GetDParameter(self, node, id, flags):
        """Called by Cinema 4D, when GetParameter is call from the node. 

        The main purpose is to return the data for member variable. It is necessary for parameters that are not simply stored in the node's container e.g. class members.

        Args:
            node (c4d.GeListNode): The instance of the ObjectData.
            id (c4d.DescID): The parameter Id.
            flags (DESCFLAGS_GET): The input flags passed to define the operation.

        Returns:
            Union[Bool, tuple(bool, Any, DESCFLAGS_GET)]: The success status or the data to be returned.
        """
        # Retrieves the parameter ID requested
        paramID = id[0].id

        # Retrieves the parameters count
        parametersLen = len(self.parameters)

        # Checks passed parameter ID is a dynamic parameter
        if OPYDYNAMICPARAMETERSOBJECT_DYNAMICGROUP_FIRSTPARAMETER <= paramID <= OPYDYNAMICPARAMETERSOBJECT_DYNAMICGROUP+parametersLen:
            # Retrieves the parameter data
            data = self.parameters[paramID-OPYDYNAMICPARAMETERSOBJECT_DYNAMICGROUP_FIRSTPARAMETER]
            return True, data, flags | c4d.DESCFLAGS_GET_PARAM_GET

        return False

    def TranslateDescID(self, node, id):
        """Called by the Attribute Manager for every object and every description ID.

        Gives a NodeData plugin the opportunity to route a description ID in the description of a node to another one.

        Args:
            node (c4d.GeListNode): The instance of the ObjectData.
            id (c4d.DescID): The parameter Id.

        Returns:
            Union[Bool, tuple(bool, c4d.DescID, c4d.C4DAtom)]: The success status or the linked DescID
        """

        # Retrieves the parameter ID requested
        paramID = id[0].id

        # OPYDYNAMICPARAMETERSOBJECT_TRANSLATED_PHONG_ANGLE references the first attached Phong tag PHONGTAG_PHONG_ANGLE parameter
        if paramID == c4d.OPYDYNAMICPARAMETERSOBJECT_TRANSLATED_PHONG_ANGLE:
            # Retrieves first Phong Tag
            tag = node.GetTag(c4d.Tphong)
            if tag is None:
                return False

            # Retrieves the Phong Tag description
            flag = c4d.DESCFLAGS_DESC_NONE if c4d.GetC4DVersion() > 20000 else c4d.DESCFLAGS_DESC_0
            desc = tag.GetDescription(flag)
            if not desc:
                return False

            # Retrieve the complete DescID for the PHONGTAG_PHONG_ANGLE parameter
            # Builds a DescID with only the parameter ID
            descId = c4d.DescID(c4d.DescLevel(c4d.PHONGTAG_PHONG_ANGLE))

            # Fills DescLever type and creator
            completeId = desc.CheckDescID(descId, None)

            return True, completeId, tag

        return False

    def GetDEnabling(self, node, id, t_data, flags, itemdesc):
        """Called  by Cinema 4D to decide which parameters should be enabled or disabled (ghosted).

        Args:
            node (c4d.BaseObject): The instance of the ObjectData.
            id (c4d.DescID): The Description ID of the parameter.
            t_data (Any): The current data for the parameter.
            flags: Not used
            itemdesc (c4d.BaseContainer): The description, encoded to a container.

        Returns:
            True if the parameter should be enabled, otherwise False.
        """

        # Retrieves the actual parameter queried
        paramID = id[0].id

        # Checks if parameter is the random ID to disable
        if paramID == self.randomID:
            return False

        return True

    def GetVirtualObjects(self, op, hh):
        """This method is called automatically when Cinema 4D ask for the cache of an object. 

        This is also the place where objects have to be marked as input object by touching them (destroy their cache in order to disable them in Viewport)

        Args:
            op (c4d.BaseObject): The Python Generator c4d.BaseObject.
            hh (c4d.HierarchyHelp): Not implemented.

        Returns:
            c4d.SplineObject: The newly allocated object chain, or None if a memory error occurred.
        """
        if op is None or hh is None:
            raise RuntimeError("Failed to retrieve op or hh.")

        returnObj = c4d.BaseObject(c4d.Osphere)
        if returnObj is None:
            raise MemoryError("Failed to create a sphere.")

        phongTag = op.GetTag(c4d.Tphong)
        if phongTag is not None:
            phongTagCopy = phongTag.GetClone()
            if phongTagCopy is None:
                raise MemoryError("Failed to retrieve a clone of the phong tag.")

            returnObj.InsertTag(phongTagCopy)

        return returnObj

    def GetBubbleHelp(self, node):
        """Called by Cinema 4D to create a contextual bubble help and status bar information for the node.

        Args:
            node (c4d.BaseObject): The instance of the ObjectData.

        Returns:
            str: The bubble help string.
        """
        return "Dynamic Object Bubble Help"


if __name__ == "__main__":
    c4d.plugins.RegisterObjectPlugin(id=PLUGIN_ID,
                                     str="Py-DynamicParametersObject",
                                     g=DynamicParametersObjectData,
                                     description="opydynamicparametersobject",
                                     icon=c4d.bitmaps.InitResourceBitmap(c4d.Onull),
                                     info=c4d.OBJECT_GENERATOR)
