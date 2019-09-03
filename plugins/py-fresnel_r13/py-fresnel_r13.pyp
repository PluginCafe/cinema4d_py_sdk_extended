"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam

Description:
    - Shader, computing a fresnel effect.

Class/method highlighted:
    - ShaderData.SetExceptionColor()
    - ShaderData.Output()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21
"""
import math
import c4d

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1027089


class PyFresnel(c4d.plugins.ShaderData):
    
    def __init__(self):
        # If a Python exception occurs during the calculation of a pixel colorize this one in red for debugging purposes
        self.SetExceptionColor(c4d.Vector(1, 0, 0))

    def FaceForward(self, N, I):
        return abs((-I) * N) * N
    
    def Fresnel(self, I, N, etasqrt):
        cos_theta = I * N
        
        fuvA = etasqrt - (1.0 - (cos_theta*cos_theta))
        fuvB = abs(fuvA)
        fu2 = (fuvA + fuvB) / 2.0
        fv2 = (-fuvA + fuvB) / 2.0
        fv2sqrt = 0.0 if fv2 == 0.0 else math.sqrt(abs(fv2))
        fu2sqrt = 0.0 if fu2 == 0.0 else math.sqrt(abs(fu2))
        
        fperp_temp = ((cos_theta + fu2sqrt) * (cos_theta+fu2sqrt)) + fv2
        if fperp_temp == 0.0:
            return 1.0

        fperp2 = (((cos_theta - fu2sqrt) * (cos_theta - fu2sqrt)) + fv2) / fperp_temp
        
        fpara_temp = ((etasqrt * cos_theta + fu2sqrt) * (etasqrt * cos_theta + fu2sqrt)) + fv2sqrt * fv2sqrt
        if fpara_temp == 0.0:
            return 1.0

        fpara2 = (((etasqrt * cos_theta - fu2sqrt) * (etasqrt * cos_theta - fu2sqrt)) + -fv2sqrt * -fv2sqrt) / fpara_temp
        
        return 0.5 * (fperp2 + fpara2)
    
    def Output(self, sh, cd):
        """
        Called by Cinema 4D for each point of the visible surface of a shaded object to return the color.
        Important: No OS calls are allowed during this function. Doing so could cause a crash, since it can be called in a multi-processor context.
        :param sh: The shader node connected with this instance.
        :type sh: c4d.BaseShader
        :param cd: Channel data to use and/or modify.
        :type cd: c4d.modules.render.ChannelData
        :return: The color of the shaded from 0 = black to 1 = white
        :rtype: c4d.Vector
        """
        # If shader is computed in 3d space
        if cd.vd:
            # default IOR value
            ior = 1.6
            n = self.FaceForward(~cd.vd.bumpn, ~cd.vd.ray.v)
            fresnel = self.Fresnel(-(~cd.vd.ray.v), ~n, ior*ior)

            return c4d.Vector(fresnel)

        # If shader is computed in 2d space, return black
        else:
            return c4d.Vector(0.0)


if __name__ == '__main__':
    # String resource, see c4d_symbols.h, have to be redefined in python
    IDS_PY_FRESNEL = 10000
    c4d.plugins.RegisterShaderPlugin(PLUGIN_ID, c4d.plugins.GeLoadString(IDS_PY_FRESNEL), 0, PyFresnel, "", 0)
