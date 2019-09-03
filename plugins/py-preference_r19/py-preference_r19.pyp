"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam

Description:
    - Exposes parameters as global Preference (EDIT->Preference windows)
    - Takes care to store data in the world container, so every part of Cinema 4D can access them.

Note:
    - Filename parameter type are not supported. The recommended way is to fake them with a string and a button.

Class/method highlighted:
    - c4d.plugins.PreferenceData
    - PreferenceData.InitPreferenceValue()
    - NodeData.Init()
    - NodeData.GetDDescription()
    - NodeData.SetDParameter()
    - NodeData.GetDParameter()
    - NodeData.GetDEnabling()

Compatible:
    - Win / Mac
    - R19, R20, R21
"""
import c4d

# Unique plugin ID obtained from www.plugincafe.com
PLUGIN_ID = 1039699

# Unique plugin ID for world preference container obtained from www.plugincafe.com
WPREF_PYPREFERENCE = 1039700

# ID for the World Preference Container parameter
WPREF_PYPREFERENCE_CHECK = 1000
WPREF_PYPREFERENCE_NUMBER = 1001


class PreferenceHelper(object):

    @staticmethod
    def GetPreferenceContainer():
        """
        Helper method to retrieve or create the WPREF_PYPREFERENCE container instance stored in the world container.
        :return: The container instance stored in the world container.
        :rtype: c4d.BaseContainer
        :raises RuntimeError: The BaseContainer can't be retrieved.
        :raises MemoryError: The BaseContainer can't be created.
        """
        # Retrieves the world container instance
        world = c4d.GetWorldContainerInstance()
        if world is None:
            raise RuntimeError("Failed to retrieve the world container instance.")

        # Retrieves the container of our plugin, stored in the world container instance
        # Parameter values will be stored in this container.
        bc = world.GetContainerInstance(WPREF_PYPREFERENCE)

        # If there is no container, creates one
        if bc is None:
            # Defines an empty container
            world.SetContainer(WPREF_PYPREFERENCE, c4d.BaseContainer())

            # Retrieves this empty container instance
            bc = world.GetContainerInstance(WPREF_PYPREFERENCE)
            if bc is None:
                raise MemoryError("Failed to create a BaseContainer.")

        return bc

    def InitValues(self, descId, description=None):
        """
        Helper method to define type and default value of parameter
        :param id: The parameter ID describing the type and the ID of the parameter you want to initialize.
        :type id: c4d.DescID
        :param description: The description of the PreferenceData.
        :type description: c4d.Description
        :return: True if success otherwise False.
        """
        # Retrieves the world BaseContainer of this preference, where values have to be defined
        bc = self.GetPreferenceContainer()

        # Defines default values
        paramId = descId[0].id
        if paramId == c4d.PYPREFERENCE_CHECK:
            self.InitPreferenceValue(WPREF_PYPREFERENCE_CHECK, True, description, descId, bc)
        elif paramId == c4d.PYPREFERENCE_NUMBER:
            self.InitPreferenceValue(WPREF_PYPREFERENCE_NUMBER, 10, description, descId, bc)

        return True


class Preference(c4d.plugins.PreferenceData, PreferenceHelper):

    def Init(self, node):
        """
        Called by Cinema 4D on the initialization of the PreferenceData, the place to define the type of object.
        :param node: The instance of the PreferenceData.
        :type node: c4d.GeListNode
        :return: True if the initialisation success, otherwise False will not create the object.
        """

        # Init default values
        self.InitValues(c4d.DescID(c4d.DescLevel(c4d.PYPREFERENCE_CHECK, c4d.DTYPE_BOOL, 0)))
        self.InitValues(c4d.DescID(c4d.DescLevel(c4d.PYPREFERENCE_NUMBER, c4d.DTYPE_LONG, 0)))

        return True

    def GetDDescription(self, node, description, flags):
        """
        Called by Cinema 4D when the description (UI) is queried.
        :param node: The instance of the PreferenceData.
        :type node: c4d.GeListNode
        :param description: The description to modify.
        :type description: c4d.Description
        :param flags:
        :return: The success status or the data to be returned.
        :rtype: Union[Bool, tuple(bool, Any, DESCFLAGS_DESC)]
        """
        # Loads description for this objects
        if not description.LoadDescription("pypreference"):
            return False

        # If default values are asked (right click on the description), defines the default values
        if flags & c4d.DESCFLAGS_DESC_NEEDDEFAULTVALUE:
            self.InitValues(c4d.DescID(c4d.DescLevel(c4d.PYPREFERENCE_CHECK, c4d.DTYPE_BOOL, 0)), description)
            self.InitValues(c4d.DescID(c4d.DescLevel(c4d.PYPREFERENCE_NUMBER, c4d.DTYPE_LONG, 0)), description)

        return True, flags | c4d.DESCFLAGS_DESC_LOADED

    def SetDParameter(self, node, id, data, flags):
        """
        Called by Cinema 4D, when SetParameter is call from the node.
        The main purpose is to store the data in the world container.
        :param node: The instance of the PreferenceData.
        :type node: c4d.GeListNode
        :param id: The parameter Id.
        :type id: c4d.DescID
        :param data: the data, the user defines and we have to store.
        :type data: Any
        :param flags: The input flags passed to define the operation.
        :type flags: DESCFLAGS_SET
        :return: The success status or the data to be returned.
        :rtype: Union[Bool, tuple(bool, Any, DESCFLAGS_SET)]
        """
        # Retrieves the world BaseContainer of this preference, where values have to be defined
        bc = self.GetPreferenceContainer()

        # Retrieves the parameter ID changed
        paramID = id[0].id

        # Store the values in the World Container
        if paramID == c4d.PYPREFERENCE_CHECK:
            bc.SetBool(WPREF_PYPREFERENCE_CHECK, data)
            return True, flags | c4d.DESCFLAGS_SET_PARAM_SET
        elif paramID == c4d.PYPREFERENCE_NUMBER:
            bc.SetInt32(WPREF_PYPREFERENCE_NUMBER, data)
            return True, flags | c4d.DESCFLAGS_SET_PARAM_SET

        return False

    def GetDParameter(self, node, id, flags):
        """
        Called by Cinema 4D, when GetParameter is call from the node.
        The main purpose is to return the data from the world container.
        :param node: The instance of the PreferenceData.
        :type node: c4d.GeListNode
        :param id: The parameter Id.
        :type id: c4d.DescID
        :param flags: The input flags passed to define the operation.
        :type flags: DESCFLAGS_GET
        :return: The success status or the data to be returned.
        :rtype: Union[Bool, tuple(bool, Any, DESCFLAGS_GET)]
        """
        # Retrieves the world BaseContainer of this preference, where values have to be retrieved
        bc = self.GetPreferenceContainer()

        # Retrieves the parameter ID asked
        paramID = id[0].id

        # Returns the values from the World Container
        if paramID == c4d.PYPREFERENCE_CHECK:
            return True, bc.GetBool(WPREF_PYPREFERENCE_CHECK), flags | c4d.DESCFLAGS_GET_PARAM_GET
        elif paramID == c4d.PYPREFERENCE_NUMBER:
            return True, bc.GetInt32(WPREF_PYPREFERENCE_NUMBER), flags | c4d.DESCFLAGS_GET_PARAM_GET

        return False

    def GetDEnabling(self, node, id, t_data, flags, itemdesc):
        """
        Called  by Cinema 4D to decide which parameters should be enabled or disabled (ghosted).
        :param node: The instance of the PreferenceData.
        :type node: c4d.GeListNode
        :param id: The Description ID of the parameter.
        :type id: c4d.DescID
        :param t_data: The current data for the parameter.
        :type: t_data: Any.
        :param flags: Not used
        :param itemdesc: The description, encoded to a container.
        :type itemdesc: c4d.BaseContainer
        :return: True if the parameter should be enabled, otherwise False.
        """
        # Retrieves the parameter ID asked
        paramID = id[0].id

        # Check box is always enable
        if paramID == c4d.PYPREFERENCE_CHECK:
            return True

        # Number is enable only if the checkbox is enable
        elif paramID == c4d.PYPREFERENCE_NUMBER:
            # Retrieves the world BaseContainer of this preference, where values have to be retrieved
            bc = self.GetPreferenceContainer()

            # Returns the state value of the checkbox
            return bc.GetBool(WPREF_PYPREFERENCE_CHECK)

        return False


if __name__ == '__main__':
    c4d.plugins.RegisterPreferencePlugin(id=PLUGIN_ID,
                                         g=Preference,
                                         name="Py-Preference",
                                         description="pypreference",
                                         parentid=0,
                                         sortid=0)
