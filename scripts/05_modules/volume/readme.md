# Volume

The Volume module allows to import and edit OpenVDB data.

Classic API:
- **c4d.VolumeObject**: *A volume in a scene.*
- **c4d.VolumeBuilder**: *A scene object (a generator) used to create volumes.*

Maxon API:
- **maxon.frameworks.volume**: *The main module to handle c4d.VolumeObject directly.*
- **maxon.frameworks.volume.VolumeToolsInterface**: *Helper interface to handle volumes.*
- **maxon.frameworks.volume.GridAccessorInterface**: *Interface to iterate volumes.*

## Examples

### gridaccessor_read
Version: R20, R21, S22, R23 - Win/Mac

    Reads the Float value of the first channel available from a Volume stored in a Volume Builder.

### gridaccessor_write
Version: R20, R21, S22, R23 - Win/Mac

    Creates a volume from scratch and assign values to voxels.

### volumebuilder_access_volume
Version: R20, R21, S22, R23 - Win/Mac

    Retrieves a volume object from a volume builder.

### volumebuilder_add_object
Version: R20, R21, S22, R23 - Win/Mac

    Creates a volume builder and adds a cube object to it. Configures cube's object settings.

### volumebuilder_create
Version: R20, R21, S22, R23 - Win/Mac

    Creates a volume builder and inserts it into the active document.

### volumebuilder_loops_inputs
Version: R20, R21, S22, R23 - Win/Mac

    Iterates over all input of a Volume Builder.

### volumecommand_create_sphere_volume
Version: R20, R21, S22, R23 - Win/Mac

    Creates a sphere volume with the corresponding command.

### volumecommand_spline_to_volume
Version: R20, R21, S22, R23 - Win/Mac

    Creates a volume from the selected spline object.
    
### volumeinterface_create_from_vdb
Version: R21, S22, R23 - Win/Mac

    Asks for a VDB file to load into a VolumeRef (a VolumeInterface Reference).
    Insert this VolumeRef into a VolumeObject.
    Inserts this VolumeObject into the current scene.

### volumetools_bool_2_mesh
Version: R20, R21, S22, R23 - Win/Mac

    Converts a Polygon Object to a Volume.
    Does a boolean operation over two Volume objects.
    Converts the resulting volume into a Polygon Object.
   
### volumetools_convert_vector_to_fog
Version: R21, S22, R23 - Win/Mac

    Creates a vector volume from scratch.
    Converts this vector volume to a fog volume.
    Inserts this fog volume as a child of a volume mesher.

### volumetools_create_curl
Version: R21, S22, R23 - Win/Mac

    Creates a new vector volume object with a curl filter applied from an existing Volume Builder set as vector mode.

### volumetools_create_gradient_sphere
Version: R20, R21, S22, R23 - Win/Mac

    Creates a Spherical Volume filled with gradient data.

### volumetools_export_mesh_to_vdb
Version: R20, R21, S22, R23 - Win/Mac

    Converts a Polygon Object to a Volume and save this volume to a VDB File.
    Save a VDB file.

### volumetools_import_vdb
Version: R20, R21, S22, R23 - Win/Mac

    Loads a VDB file to a c4d.VolumeObject.

### volumetools_meshtovolume_volumetomesh
Version: R20, R21, S22, R23 - Win/Mac

    Converts a Polygon Object to a Volume and convert it back to a Polygon Object.

### volumetools_mix_2_mesh
Version: R20, R21, S22, R23 - Win/Mac

    Converts a Polygon Object to a FOG Volume.
    Does a mix operation over two FOG Volume objects.
    Converts the resulting FOG volume into a Polygon Object.

### volumetools_mix_vector_volumes
Version: R21, S22, R23 - Win/Mac

    Creates 2 vector volume from scratch.
    Mixes both vector volumes with a cross product to produce a third vector volume.
    Inserts all 3 volumes into the scene.
