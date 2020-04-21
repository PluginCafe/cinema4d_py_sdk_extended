# Motion Tracker

The Motion Tracker API provides read-only access to properties of the Motion Tracker object.\
It is possible to access information on the loaded footage and on the created 2D tracks.

Classic API:
- **c4d.modules.motiontracker**: *The module which provides classes to use the Motion Tracker Libraries.*
- **c4d.modules.motiontracker.MotionTrackerObject**: *Represents a Motion Tracker object in the scene.*
- **c4d.modules.motiontracker.MtFootageData**: *Stores information on the loaded video footage.*
- **c4d.modules.motiontracker.Mt2dTrackData**: *Provides access to the 2D tracking data.*
- **c4d.modules.motiontracker.Mt2dTrack**: *Represents one 2D track.*
- **c4d.modules.motiontracker.MtData**: *Stores information of the Mt2dTrack.*

## Examples

### motiontracker_get_2dtrack_from_object
Version: R18, R19, R20, R21, S22 - Win/Mac

    Loops through all the tracks of the active Motion Tracker object.

