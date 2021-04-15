# Description

A parameter description includes the type of a parameter and some additional information. Such a parameter description is stored in a BaseContainer. The different settings are accessed using the IDs described on this page. 
These settings define how the parameter behaves and how it is displayed in the Attribute Manager.

Classic API:
- **c4d.Description**: *The description class contains information for all description ID of an object.*
- **c4d.DescID**: *Parameters of C4DAtom based elements are identified using a DescID object. Such a DescID object is composed of one or several levels of DescLevel objects.*
- **c4d.DescLevel**: *Represents a level of a DescID parameter ID.*

## Examples

### description_check_descid

    Retrieves a complete DescID (with datatype and creator IDs) from another DescID.

### description_create_popup_menu

    Retrieves a BaseContainer with all the parameters of an object.
    
### description_getsubdescriptionwithdata

    Retrieves SubDescription parameters information.
