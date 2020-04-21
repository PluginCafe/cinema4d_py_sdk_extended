"""
Copyright: MAXON Computer GmbH

Description:
    - Creates and define a noise shader as an input of a Voronoi Fracture object.

Class/method highlighted:
    - c4d.VoronoiFracture
    - VoronoiFracture.AddPointGenerator()

Compatible:
    - Win / Mac
    - R18, R19, R20, R21, S22
"""
import c4d


def main():
    # Creates Voronoi Fracture object and inserts it into the active document
    voronoi = c4d.VoronoiFracture()
    if voronoi is None:
        raise MemoryError("Failed to create a Voronoi Fracture object.")
    doc.InsertObject(voronoi)

    # Creates Cube object and inserts it into the active document
    cube = c4d.BaseObject(c4d.Ocube)
    if cube is None:
        raise MemoryError("Failed to create a cube.")
    doc.InsertObject(cube)

    # Makes it editable and finally insert it as child of Voronoi Fracture object
    editable = c4d.utils.SendModelingCommand(c4d.MCOMMAND_MAKEEDITABLE, list=[cube], mode=c4d.MODIFY_ALL, doc=doc)
    if not editable:
        raise RuntimeError("Failed to do the SendModelingCommand operation.")
    doc.InsertObject(editable[0], parent=voronoi)

    # Adds a point generator
    ret = voronoi.AddPointGenerator(c4d.ID_POINTCREATOR_CREATORTYPE_DISTRIBUTION)
    if ret is None:
        raise MemoryError("Failed to create a new point generator.")
    generator = ret[0]
    generator[c4d.ID_POINTCREATOR_CREATEDPOINTAMOUNT] = 25
    generator[c4d.ID_POINTCREATOR_CREATEPOINTSSEED] = 73519

    # Adds a shader generator
    ret = voronoi.AddPointGenerator(c4d.ID_POINTCREATOR_CREATORTYPE_SHADER)
    if ret is None:
        raise MemoryError("Failed to create a new point generator.")
    generator = ret[0]

    # Setups Noise shader
    noise = c4d.BaseShader(c4d.Xnoise)
    if noise is None:
        raise MemoryError("Failed to create a noise shader.")
    noise[c4d.SLA_NOISE_NOISE] = c4d.NOISE_OFFSET + c4d.NOISE_VORONOI_3

    # Sets the shader for the generator
    generator[c4d.ID_POINTCREATOR_SHADER_SHADER] = noise
    generator.InsertShader(noise)
    generator.Message(c4d.MSG_UPDATE)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
