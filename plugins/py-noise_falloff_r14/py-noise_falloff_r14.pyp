"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam

Description:
    - Falloff, modify how effector sampling occurs in this case using a noise (like the spherical falloff).
    - Falloff are deprecated in R20 and replaced by Fields, but Falloff keep working for compatibility reason.
    - Manages handles to drive parameters.

Class/method highlighted:
    - c4d.plugins.FalloffData
    - FalloffData.Init()
    - FalloffData.InitFalloff()
    - FalloffData.GetDVisible()
    - FalloffData.Sample()
    - FalloffData.GetHandleCount()
    - FalloffData.GetHandle()
    - FalloffData.SetHandle()
    - FalloffData.Draw()

"""
import c4d

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1028347


class NoiseFalloffHelper(object):
    """Utility class for the noise falloff"""

    @staticmethod
    def PointInBox(p, data):
        """Returns if a point is in box.

        Args:
            p (c4d.Vector): The point position.
            data (c4d.BaseContainer): Falloff data information.

        Returns:
            True if the point is in box, otherwise False
        """
        res = True

        point = [p.x, p.y, p.z]

        size = data.size * data.nodemat * data.scale
        size -= data.nodemat.off
        size = [size.x, size.y, size.z]

        offset = [data.offset.x, data.offset.y, data.offset.z]

        pos = c4d.Vector() * data.nodemat
        pos = [pos.x, pos.y, pos.z]

        for i in range(3):
            res = pos[i] + offset[i] + size[i] > point[i] > pos[i] + offset[i] - size[i]
            if not res:
                break

        return res

    @staticmethod
    def DrawHandleLines(bd, size, i):
        """Helper method to draw a handle.

        Args:
            bd (c4d.BaseDraw): The editor's view.
            size (c4d.Vector): vector size of the object
            i (int): The Handle Id
        """

        # Defines the Draw Color
        bd.SetPen(c4d.GetViewColor(c4d.VIEWCOLOR_ACTIVEPOINT))

        # According the handle id, defines start/end of the line handle
        p1, p2, p3, p4 = c4d.Vector(), c4d.Vector(), c4d.Vector(), c4d.Vector()

        if i == 0:
            p1 = c4d.Vector(0, -size.y, -size.z)
            p2 = c4d.Vector(0, -size.y, size.z)
            p3 = c4d.Vector(0, size.y, size.z)
            p4 = c4d.Vector(0, size.y, -size.z)

        elif i == 1:
            p1 = c4d.Vector(-size.x, 0, -size.z)
            p2 = c4d.Vector(-size.x, 0, size.z)
            p3 = c4d.Vector(size.x, 0, size.z)
            p4 = c4d.Vector(size.x, 0, -size.z)

        elif i == 2:
            p1 = c4d.Vector(-size.x, -size.y, 0)
            p2 = c4d.Vector(-size.x, size.y, 0)
            p3 = c4d.Vector(size.x, size.y, 0)
            p4 = c4d.Vector(size.x, -size.y, 0)

        # Draws each line as a grid
        bd.DrawLine(p1, p2, 0)
        bd.DrawLine(p2, p3, 0)
        bd.DrawLine(p3, p4, 0)
        bd.DrawLine(p4, p1, 0)


class NoiseFalloff(c4d.plugins.FalloffData, NoiseFalloffHelper):
    """Noise Falloff"""
    
    HANDLECOUNT = 6
    FBM_TYPES = (c4d.NOISE_ZADA, c4d.NOISE_DISPL_VORONOI, c4d.NOISE_OBER, c4d.NOISE_FBM, c4d.NOISE_BUYA)

    seed = 1234567
    noise = c4d.utils.noise.C4DNoise()
    type = c4d.NOISE_BOX_NOISE
    octaves = 4.0
    absolute = False
    sampling = True
    sampleRad = 0.25
    detailAtt = 0.25
    repeat = 0
    maxoctave = 21
    lacunarity = 2.1
    h = 0.5
    
    dirty = 0

    def Init(self, falldata, bc):
        """Called when Cinema 4D Initialize the Falloff Object (used to define, default values).

        Args:
            falldata (c4d.modules.mograph.FalloffDataData): Falloff data information.
            bc (c4d.BaseContainer): Falloff's container.

        Returns:
            True on success, otherwise False.
        """
        if bc is None:
            return False

        # Defines defaults values in the BaseContainer if tey are not already sets
        if bc.GetData(c4d.PYNOISEFALLOFF_SEED) is None:
            bc.SetInt32(c4d.PYNOISEFALLOFF_SEED, 1234567)
        
        if bc.GetData(c4d.PYNOISEFALLOFF_TYPE) is None:
            bc.SetInt32(c4d.PYNOISEFALLOFF_TYPE, c4d.NOISE_BOX_NOISE)
        
        if bc.GetData(c4d.PYNOISEFALLOFF_SAMPRAD) is None:
            bc.SetFloat(c4d.PYNOISEFALLOFF_SAMPRAD, 0.25)
        
        if bc.GetData(c4d.PYNOISEFALLOFF_DETATT) is None:
            bc.SetFloat(c4d.PYNOISEFALLOFF_DETATT, 0.25)
        
        if bc.GetData(c4d.PYNOISEFALLOFF_OCTAVES) is None:
            bc.SetFloat(c4d.PYNOISEFALLOFF_OCTAVES, 4.0)
        
        if bc.GetData(c4d.PYNOISEFALLOFF_ABSOLUTE) is None:
            bc.SetBool(c4d.PYNOISEFALLOFF_ABSOLUTE, False)
        
        if bc.GetData(c4d.PYNOISEFALLOFF_MAXOCTAVE) is None:
            bc.SetInt32(c4d.PYNOISEFALLOFF_MAXOCTAVE, 21)
        
        if bc.GetData(c4d.PYNOISEFALLOFF_LACUNARITY) is None:
            bc.SetFloat(c4d.PYNOISEFALLOFF_LACUNARITY, 2.1)
        
        if bc.GetData(c4d.PYNOISEFALLOFF_H) is None:
            bc.SetFloat(c4d.PYNOISEFALLOFF_H, 0.5)
        
        return True

    def InitFalloff(self, bc, falldata):
        """Called when Cinema 4D initialize the Falloff (Before a sampling process).

        Args:
            bc (c4d.BaseContainer): Falloff's container.
            falldata (c4d.modules.mograph.FalloffDataData): Falloff data information.

        Returns:
            True on success, otherwise False.
        """
        if bc is None:
            return False

        # If the dirtiness of the BaseContainer didn't change, simply returns
        dirty = bc.GetDirty()
        if self.dirty == dirty:
            return True

        # Retrieves parameters from the falloff object to the python object
        self.seed = bc.GetInt32(c4d.PYNOISEFALLOFF_SEED)
        self.type = bc.GetInt32(c4d.PYNOISEFALLOFF_TYPE)
        self.octaves = bc.GetFloat(c4d.PYNOISEFALLOFF_OCTAVES)
        self.absolute = bc.GetBool(c4d.PYNOISEFALLOFF_ABSOLUTE)
        self.sampling = bc.GetInt32(c4d.PYNOISEFALLOFF_SAMPLING) is 0
        self.sampleRad = bc.GetFloat(c4d.PYNOISEFALLOFF_SAMPRAD)
        self.detailAtt = bc.GetFloat(c4d.PYNOISEFALLOFF_DETATT)
        self.repeat = bc.GetInt32(c4d.PYNOISEFALLOFF_REPEAT)

        self.maxoctave = bc.GetInt32(c4d.PYNOISEFALLOFF_MAXOCTAVE)
        self.lacunarity = bc.GetFloat(c4d.PYNOISEFALLOFF_LACUNARITY)
        self.h = bc.GetInt32(c4d.PYNOISEFALLOFF_H)

        # Initializes the noise if needed
        self.noise = c4d.utils.noise.C4DNoise(seed=self.seed)
        if self.type in self.FBM_TYPES:
            self.noise.InitFbm(self.maxoctave, self.lacunarity, self.h)

        self.dirty = dirty

        return True

    def GetDVisible(self, id, bc, desc_bc):
        """Called  by Cinema 4D to decide which parameters is currently visible.

        Args:
            id (c4d.DescID): The Description ID of the parameter
            bc (c4d.BaseContainer): Falloff's container
            desc_bc (c4d.BaseContainer): The description, encoded to a container

        Returns:
            True if the parameter should be visible, otherwise False.
        """

        # Displays Octave only if current noise have Octave
        if id[0].id == c4d.PYNOISEFALLOFF_OCTAVES:
            return self.noise.HasOctaves(bc.GetInt32(c4d.PYNOISEFALLOFF_TYPE))

        # Displays Absolute only if current noise have Absolute
        elif id[0].id == c4d.PYNOISEFALLOFF_ABSOLUTE:
            return self.noise.HasAbsolute(bc.GetInt32(c4d.PYNOISEFALLOFF_TYPE))

        # Displays fbm types only if current noise have fbm
        elif id[0].id == c4d.PYNOISEFALLOFF_FBMSETTINGS:
            return bc.GetInt32(c4d.PYNOISEFALLOFF_TYPE) in self.FBM_TYPES

        # For any other parameters, display it
        return True
    
    def Sample(self, p, data):
        """Called by Cinema 4D, when a position is sampled.

        Args:
            p (c4d.Vector): The position of the point to sample in falloff space.
            data (c4d.modules.mograph.FalloffDataData): Falloff data information.

        Returns:
            float: How the effector modify the original object from 0.0 to 1.0
        """
        # If the point is in the bounding box of the falloff
        if NoiseFalloff.PointInBox(data.mat * p, data):
            return self.noise.Noise(self.type, self.sampling, data.mat * p, 0.0, self.octaves, self.absolute, self.sampleRad, self.detailAtt, self.repeat)
        else:
            return 1.0
    """========== Start of Handle Management =========="""

    def GetHandleCount(self, bc, data):
        """Called by Cinema 4D to retrieve the count of Handle the object will have.

        Args:
            bc (c4d.BaseContainer): Falloff's container
            data (c4d.modules.mograph.FalloffDataData): Falloff data information.

        Returns:
            int: The number of handle
        """
        return self.HANDLECOUNT

    def GetHandle(self, bc, i, info, data):
        """Called by Cinema 4D to retrieve the information of a given handle ID to represent a/some parameter(s).

        Args:
            bc (c4d.BaseContainer): Falloff's container
            i (int): The handle index.
            data (c4d.modules.mograph.FalloffDataData): Falloff data information.
            info (c4d.HandleInfo): The information for the requested handle to be filled.
        """
        if bc is None:
            return

        # Retrieves the current size, offset from noise parameter
        size = bc.GetVector(c4d.FALLOFF_SIZE) * bc.GetFloat(c4d.FALLOFF_SCALE)
        offset = bc.GetVector(c4d.FALLOFF_SHAPE_OFFSET)

        # Regarding the orientation, defines position / direction of the handle
        if i == c4d.FALLOFF_SHAPE_AXIS_XP:
            info.position = c4d.Vector(size.x + offset.x, offset.y, offset.z)
            info.direction = c4d.Vector(1.0, 0.0, 0.0)
        elif i == c4d.FALLOFF_SHAPE_AXIS_XN:
            info.position = c4d.Vector(-size.x + offset.x, offset.y, offset.z)
            info.direction = c4d.Vector(-1.0, 0.0, 0.0)
        elif i == c4d.FALLOFF_SHAPE_AXIS_YP:
            info.position = c4d.Vector(offset.x, size.y + offset.y, offset.z)
            info.direction = c4d.Vector(0.0, 1.0, 0.0)
        elif i == c4d.FALLOFF_SHAPE_AXIS_YN:
            info.position = c4d.Vector(offset.x, -size.y + offset.y, offset.z)
            info.direction = c4d.Vector(0.0, -1.0, 0.0)
        elif i == c4d.FALLOFF_SHAPE_AXIS_ZP:
            info.position = c4d.Vector(offset.x, offset.y, size.z + offset.z)
            info.direction = c4d.Vector(0.0, 0.0, 1.0)
        elif i == c4d.FALLOFF_SHAPE_AXIS_ZN:
            info.position = c4d.Vector(offset.x, offset.y, -size.z + offset.z)
            info.direction = c4d.Vector(0.0, 0.0, -1.0)

        info.type = c4d.HANDLECONSTRAINTTYPE_LINEAR
    
    def SetHandle(self, bc, i, p, data):
        """Called by Cinema 4D when the user set the handle.

        This is the place to retrieve the information of a given handle ID and drive your parameter(s).

        Args:
            bc (c4d.BaseContainer): Falloff's container
            i (int): The handle index.
            p (c4d.Vector): The new Handle Position.
            data (c4d.modules.mograph.FalloffDataData): Falloff data information.
        """
        if bc is None:
            return False

        # Retrieves the Falloff size
        size = bc.GetVector(c4d.FALLOFF_SIZE)

        # According the moved handles retrieves the position
        if i == 0 or i == 1:
            size = c4d.Vector(abs(p.x), size.y, size.z)
        elif i == 2 or i == 3:
            size = c4d.Vector(size.x, abs(p.y), size.z)
        elif i == 4 or i == 5:
            size = c4d.Vector(size.x, size.y, abs(p.z))

        # Defines the size vector
        bc.SetVector(c4d.FALLOFF_SIZE, size)

    def Draw(self, data, drawpass, bd, bh):
        """Called by Cinema 4D when the display is updated to display.

        Here you can draw visual representations and handles for your object in the 3D view.

        Args:
            data (c4d.BaseContainer.): The node settings container.
            op (c4d.modules.mograph.FalloffDataData): Falloff data information.
            drawpass (DRAWPASS): The current draw pass.
            bd (c4d.BaseDraw): The editor's view.
            bh (c4d.plugins.BaseDrawHelp): The BaseDrawHelp editor's view.

        Returns:
            The result of the drawing (most likely c4d.DRAWRESULT_OK)
        """
        # If the current draw pass is not the handle, skip this Draw Call.
        if drawpass == c4d.DRAWPASS_HIGHLIGHTS:
            return True

        # Defines the size and the position of the object
        size = data.size * data.scale
        mat = c4d.Matrix(data.nodemat.off+data.offset, data.nodemat.v1, data.nodemat.v2, data.nodemat.v3)

        # Defines the drawing matrix to the object matrix
        bd.SetMatrix_Matrix(None, mat)

        # Draws the overall bounding box
        box = c4d.Matrix()
        box.v1 = box.v1 * size.x
        box.v2 = box.v2 * size.y
        box.v3 = box.v3 * size.z
        bd.DrawBox(box, 1.0, c4d.GetViewColor(c4d.VIEWCOLOR_ACTIVEPOINT), True)

        # Draws each handles
        NoiseFalloff.DrawHandleLines(bd, size, 0)
        NoiseFalloff.DrawHandleLines(bd, size, 1)
        NoiseFalloff.DrawHandleLines(bd, size, 2)
        
        return True
    """========== End of Handle Management =========="""


if __name__ == "__main__":
    # Registers the Falloff Plugin
    c4d.plugins.RegisterFalloffPlugin(id=PLUGIN_ID,
                                      str="Py-NoiseFalloff",
                                      info=0,
                                      g=NoiseFalloff,
                                      description="Ofalloff_pynoise")
