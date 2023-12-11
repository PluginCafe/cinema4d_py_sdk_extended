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

"""
import c4d

# Unique plugin ID obtained from www.plugincafe.com
PLUGIN_ID = 1039699

# Unique plugin ID for world preference container obtained from www.plugincafe.com
WPREF_PYPREFERENCE = 1039700

# ID for the World Preference Container parameter
WPREF_PYPREFERENCE_CHECK = 1000
WPREF_PYPREFERENCE_NUMBER = 1001


# The first time Cinema 4D will compile this script into Python Bytecode, symbols will not be yet parsed.
# This will cause PYPREFERENCE_CHECK and PYPREFERENCE_NUMBER not defined in the c4d module.
# Thats why we manually do it (numbers are defined in res/description/pypreference.h)
if not hasattr(c4d, "PYPREFERENCE_CHECK"):
    c4d.PYPREFERENCE_CHECK = 1000

if not hasattr(c4d, "PYPREFERENCE_NUMBER"):
    c4d.PYPREFERENCE_NUMBER = 1001


class PreferenceHelper(object):

    @staticmethod
    def GetPreferenceContainer():
        """Helper method to retrieve or create the WPREF_PYPREFERENCE container instance stored in the world container.

        Returns:
            c4d.BaseContainer: The container instance stored in the world container.

        Raises:
            RuntimeError: The BaseContainer can't be retrieved.
            MemoryError: The BaseContainer can't be created.
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
        """Helper method to define type and default value of parameter

        Args:
            descId (c4d.DescID): The parameter ID describing the type and the ID of the parameter you want to initialize.
            description (c4d.Description, optional): The description of the PreferenceData. Defaults to None.

        Returns:
            True if success otherwise False.
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

    def Init(self, node, isCloneInit=False):
        """Called by Cinema 4D on the initialization of the PreferenceData, the place to define the type of object.

        Args:
            node (c4d.GeListNode): The instance of the PreferenceData.
            isCloneInit (bool): True if the preference data is a copy of another one.

        Returns:
            True if the initialization success, otherwise False will not create the object.
        """

        # Init default values
        self.InitValues(c4d.DescID(c4d.DescLevel(c4d.PYPREFERENCE_CHECK, c4d.DTYPE_BOOL, 0)))
        self.InitValues(c4d.DescID(c4d.DescLevel(c4d.PYPREFERENCE_NUMBER, c4d.DTYPE_LONG, 0)))

        return True

    def GetDDescription(self, node, description, flags):
        """Called by Cinema 4D when the description (UI) is queried.

        Args:
            node (c4d.GeListNode): The instance of the PreferenceData.
            description (c4d.Description): The description to modify.
            flags (int): The flags for the description operation.

        Returns:
            Union[Bool, tuple(bool, Any, DESCFLAGS_DESC)]: The success status or the data to be returned.
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
        """Called by Cinema 4D, when SetParameter is call from the node.

        The main purpose is to store the data in the world container.

        Args:
            node (c4d.GeListNode): The instance of the PreferenceData.
            id (c4d.DescID): The parameter Id.
            data (Any): the data, the user defines and we have to store.
            flags (DESCFLAGS_SET): The input flags passed to define the operation.

        Returns:
            Union[Bool, tuple(bool, Any, DESCFLAGS_SET)]: The success status or the data to be returned.
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
        """Called by Cinema 4D, when GetParameter is call from the node.
        
        The main purpose is to return the data from the world container.

        Args:
            node (c4d.GeListNode): The instance of the PreferenceData.
            id (c4d.DescID): The parameter Id.
            flags (DESCFLAGS_GET): The input flags passed to define the operation.

        Returns:
            Union[Bool, tuple(bool, Any, DESCFLAGS_GET)]: The success status or the data to be returned.
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
        """Called  by Cinema 4D to decide which parameters should be enabled or disabled (ghosted).

        Args:
            node (c4d.GeListNode): The instance of the PreferenceData.
            id (c4d.DescID): The Description ID of the parameter.
            t_data (Any.): The current data for the parameter.
            flags: Not used
            itemdesc (c4d.BaseContainer): The description, encoded to a container.

        Returns:
            True if the parameter should be enabled, otherwise False.
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
