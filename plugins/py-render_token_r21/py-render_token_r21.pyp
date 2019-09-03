"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Registers two Tokens plugin. One visible in the render setting the other one not.
    - A token is a string that will be replaced during the token evaluation time by a string representation.

Class/method highlighted:
    - c4d.plugins.RegisterToken
    - c4d.plugins.RegisterHiddenToken

Compatible:
    - Win / Mac
    - R21
"""
import c4d


def PythonToken(data):
    """
    The function that will be called to return the string representation of a token.

    :param data: A BaseContainer filled with some informative data

        data[0],  # The BaseDocument used for rendering, can be a clone of the original document.
        data[1],  # The RenderData used for rendering.
        data[2],  # The BaseContainer with the render settings (can be different from _rData->GetDataInstance()).
        data[3],  # The BaseTake used for rendering.
        data[4],  # The frame number used for rendering or NOTOK if the frame is not yet recognized.
        data[5],  # The pass user name if multipass is activated.
        data[6],  # The pass type name if multipass is activated.
        data[7],  # The pass ID used for rendering or NOTOK if multipass is not active or not yet recognized.
        data[8],  # True if the pass is a separated light pass.
        data[9],  # The light number id.
        data[10],  # True if the pass is a separated reflectance material pass.
        data[11],  # if _isLight is True or _isMaterial is True store here the object scene name.
        data[12],  # if True warning strings will be used for the Tokens that cannot be resolved.
        data[13])  # An owner node for certain tokens such as MoGraph cache tokens.

    :type data: c4d.BaseContainer
    :return: The string that will replace the token
    :rtype: str
    """

    # Returns the frame number as a string. So this will replace the token by the frame number.
    return str(data[4])

def PythonHiddenToken(data):
    """
    The function that will be called to return the string representation of a token.

    :param data: A BaseContainer filled with some informative data

        data[0],  # The BaseDocument used for rendering, can be a clone of the original document.
        data[1],  # The RenderData used for rendering.
        data[2],  # The BaseContainer with the render settings (can be different from _rData->GetDataInstance()).
        data[3],  # The BaseTake used for rendering.
        data[4],  # The frame number used for rendering or NOTOK if the frame is not yet recognized.
        data[5],  # The pass user name if multipass is activated.
        data[6],  # The pass type name if multipass is activated.
        data[7],  # The pass ID used for rendering or NOTOK if multipass is not active or not yet recognized.
        data[8],  # True if the pass is a separated light pass.
        data[9],  # The light number id.
        data[10],  # True if the pass is a separated reflectance material pass.
        data[11],  # if _isLight is True or _isMaterial is True store here the object scene name.
        data[12],  # if True warning strings will be used for the Tokens that cannot be resolved.
        data[13])  # An owner node for certain tokens such as MoGraph cache tokens.

    :type data: c4d.BaseContainer
    :return: The string that will replace the token
    :rtype: str
    """

    # Returns the frame number as a string. So this will replace the token by the frame number.
    return str(data[4])


if __name__=="__main__":
    # First it's important to check if the token is not already registered
    for registeredToken in c4d.modules.tokensystem.GetAllTokenEntries():
        # Checks if the token name is already used, if it's the case exit.
        if registeredToken.get("_token") in ["PythonToken", "PythonHiddenToken"]:
            exit()

    # Registers the token "PythonToken" that will be visible in te render setting.
    c4d.plugins.RegisterToken("PythonToken", "This is a Python Token", "001", PythonToken)

    # Registers the token "PythonHiddenToken" it will not be visible in te render setting.
    c4d.plugins.RegisterHiddenToken("PythonHiddenToken", "This is a Hidden Python Token", "001", PythonHiddenToken)
