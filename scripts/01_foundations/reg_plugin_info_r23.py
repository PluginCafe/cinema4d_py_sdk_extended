"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Stores plugin information.

Class/method highlighted:
    - c4d.plugins.ReadRegInfo()
    - c4d.plugins.WriteRegInfo()
    - c4d.plugins.ReadPluginInfo()
    - c4d.plugins.WritePluginInfo()

Compatible:
    - Win / Mac
    - R23
"""
import c4d


def main():
    # Create byte data to be stored later in the RegInfo
    # The maximum allowed size is 3500 bytes
    dataBytes = b"Permanent Data"

    # Obtained from www.plugincafe.com
    uniquePluginID = 1000000

    # Write the data, use this within a license server environment
    c4d.plugins.WriteRegInfo(uniquePluginID, dataBytes)

    # Read the data, use this within a license server environment
    print(type(c4d.plugins.ReadRegInfo(uniquePluginID, 40)))

    # Write the data, Cinema 4D will store this data encrypted based on the license.
    c4d.plugins.WritePluginInfo(uniquePluginID, dataBytes)

    # Read the data
    print(c4d.plugins.ReadPluginInfo(uniquePluginID, 40))


if __name__ == "__main__":
    main()
