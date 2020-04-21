"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Demonstrates how to define custom icon color according to the new Cinema 4D R21 icon features.

Class/method highlighted:
    - MSG_GETCUSTOMICON
    - c4d.CustomIconSettings
    - maxon.BaseArray
    - maxon.Color
    - c4d.CustomIconSettings.FillCustomIconSettingsFromBaseList2D()
    - c4d.CustomIconSettings.GetCustomIcon()

Compatible:
    - Win / Mac
    - R21
"""
import os
import c4d
import maxon

PLUGIN_ID = 1053134


class CustomIconObjectData(c4d.plugins.ObjectData):

    def Init(self, node):
        """
        Called when Cinema 4D Initialize the ObjectData (used to define, default values)
        :param node: The instance of the ObjectData.
        :type node: c4d.GeListNode
        :return: True on success, otherwise False.
        """

        # Creates a BaseContainer to store all custom color mode
        iconSpecialModes = c4d.BaseContainer()

        # Additional Special Color Mode for light object
        iconSpecialModes.SetString(0, "Custom Color Mode")

        # Creates a BaseContainer to define the initial iconsetting of the object
        iconSettings = c4d.BaseContainer()

        # Defines the custom color mode used with the previously created BaseContainer already filled
        iconSettings.SetContainer(0, iconSpecialModes)

        # Since we are going to use our custom MSG_GETCUSTOMICONS code,
        # set this to True so parent object (e.g. BaseObject) will ignore MSG_GETCUSTOMICONS messages.
        iconSettings.SetBool(c4d.ID_ICONCHOOSER_SETTINGS_PARENT_IGNORE, True)

        #  Sets icon settings container into the current Object instance data container
        node.GetDataInstance().SetContainer(c4d.ID_ICONCHOOSER_SETTINGS, iconSettings)

        # Default color mode: custom mode
        node.GetDataInstance().SetInt32(c4d.ID_BASELIST_ICON_COLORIZE_MODE, c4d.ID_BASELIST_ICON_COLORIZE_MODE_CUSTOM + 1)

        return True

    def GetVirtualObjects(self, node, hh):
        """
        This method is called automatically when Cinema 4D ask for the cache of an object. This is also the place
        where objects have to be marked as input object by Touching them (destroy their cache in order to disable them in Viewport)

        :param node: The Python Generator
        :type node: c4d.BaseObject.
        :param hh: The hierarchy helper.
        :type hh: c4d.HierarchyHelp (currently a PyObject).
        :return: The Representing object
        """
        return c4d.BaseObject(c4d.Onull)

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
        if msgId == c4d.MSG_GETCUSTOMICON:
            settings = c4d.CustomIconSettings()

            # Take care due to the nature of python (settings._specialColors returns a copy)
            # so it's important to first retrieve the BaseArray and then resize it then re-assign it.
            arr = settings._specialColors
            arr.Resize(1)

            # Creates an RGB value for custom color mode
            arr[0] = maxon.Color(1, 0, 0)

            # Reassigns the BaseArray data to the CustomIconSettings
            settings._specialColors = arr

            # Fills the CustomIconSettings with the passed BaseContainer object
            c4d.CustomIconSettings.FillCustomIconSettingsFromBaseList2D(settings, node.GetData(), node.GetType(), True)

            # Finally fills the icon Data settings with the CustomIconSettings
            c4d.CustomIconSettings.GetCustomIcon(data, settings, True)
        return True


if __name__ == "__main__":
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "customicon.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    # Registers the object plugin
    c4d.plugins.RegisterObjectPlugin(id=PLUGIN_ID,
                                     str="py-Custom Icon Object Data",
                                     g=CustomIconObjectData,
                                     description="py_custom_icon",
                                     icon=bmp,
                                     info=c4d.OBJECT_GENERATOR)
