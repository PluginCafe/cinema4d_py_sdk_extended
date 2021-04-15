"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates 90 Thinking Particles.
    - Defines custom position and color for each particle.

Class/method highlighted:
    - BaseDocument.GetParticleSystem()
    - TP_MasterSystem.GetRootGroup()
    - TP_MasterSystem.AllocParticles()
    - TP_MasterSystem.SetPosition()
    - TP_MasterSystem.SetColor()

"""
import c4d


def main():
    # Retrieves the Particles System of the current document
    pSys = doc.GetParticleSystem()
    if pSys is None:
        raise RuntimeError("op is none, please select one object.")

    # Retrieves the Root group (where all particles belongs as default)
    rootGrp = pSys.GetRootGroup()
    if rootGrp is None:
        raise RuntimeError("Failed to retrieve root group of tp master system.")

    # Allows each particles to get a custom colors
    rootGrp[c4d.PGROUP_USE_COLOR] = False

    # Creates 90 Particles
    particlesIds = pSys.AllocParticles(90)
    if not particlesIds:
        raise RuntimeError("Failed to create 90 TP particles.")

    # Assigns position and colors for each particles
    for particleId in particlesIds:
        # Checks if particles ID is ok
        if particleId == c4d.NOTOK:
            continue

        # Calculates a position
        sin, cos = c4d.utils.SinCos(particleId)
        pos = c4d.Vector(sin * 100.0, cos * 100.0, particleId * 10.0)
        # Assigns position
        pSys.SetPosition(particleId, pos)

        # Calculates a color
        hsv = c4d.Vector(float(particleId) * 1.0 / 90.0, 1.0, 1.0)
        rgb = c4d.utils.HSVToRGB(hsv)

        # Assigns color
        pSys.SetColor(particleId, rgb)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
