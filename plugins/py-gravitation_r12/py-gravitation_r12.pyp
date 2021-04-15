"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam

Description:
    - Particle Modifier, applying a simple gravitation effect for each particles.

Note:
    - Only modify Cinema 4D basic particles.

Class/method highlighted:
    - c4d.plugins.ObjectData
    - ObjectData.ModifyParticles()
"""
import os
import c4d

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1025246


class Gravitation(c4d.plugins.ObjectData):
    """Gravitation Generator"""

    def ModifyParticles(self, op, pp, ss, pcnt, diff):
        """Called by Cinema 4D to modify C4D particles

        Args:
            op (c4d.BaseObject): the current modifier
            pp (c4d.modules.particles.Particle]): The initial element of the Particle list.
            ss (c4d.modules.particles.BaseParticle]): The BaseParticle List to modify
            pcnt (int): The number of particles in pp and ss list.
            diff (float): The time delta for the particles movement in seconds. Usually the difference in time between two frames, but this can be different for such functions as motion blur.
        """
        # Calculate simple gravitation
        gravitation = 918.0
        amp = diff * gravitation
        img = ~op.GetMg()

        # Iterates all particles
        for s, p in zip(pp, ss):
            # If the particle is not visible, simple go to the next one
            if not (s.bits & c4d.PARTICLEFLAGS_VISIBLE):
                continue
            
            vv = s.v3
            
            vv.y -= amp
            p.v += vv
            p.count += 1
        return


if __name__ == "__main__":
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "gravitation.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    c4d.plugins.RegisterObjectPlugin(id=PLUGIN_ID,
                                     str="Py-Gravitation",
                                     g=Gravitation,
                                     description="gravitation",
                                     icon=bmp,
                                     info=c4d.OBJECT_PARTICLEMODIFIER)
