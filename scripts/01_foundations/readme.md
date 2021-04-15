# Foundations

The classic API and MAXON API provides various fundamental concepts and classes.

Classic API:
- **c4d.C4DAtom**: *Base class for many entities in the classic Cinema 4D API.*
- **c4d.GeListNode**: *Based on C4DAtom, provides the functionality to organize elements in linked lists and trees.*
- **c4d.BaseList2D**: *Based on C4DAtom and GeListNode. It is a base class for many entities of the classic Cinema 4D API.*
- **c4d.GeListHead**: *A GeListHead object is the root of a list or tree of GeListNode elements.*
- **c4d.DescID**: *Parameters of C4DAtom based elements are identified using a DescID object.*

Maxon API:
- **maxon.Url**: *Defines the location of a file or a similar resource*.
- **maxon.InputStream**: *An input stream is used to read data from a resource defined with a maxon::Url.*
- **maxon.OutputStream**: *An output stream is used to write data to a resource defined with a maxon::Url.*

## Examples

### reg_plugin_info

    Stores plugin information.

### retrieves_temp_folder

    Retrieves the path of the preference folder according to an installation path without the need to launch Cinema 4D.

### script_custom_icon

    Example to customize the icon used for a script.

### script_custom_name_description

    Example to customize the name and the description for a script in the script manager.
