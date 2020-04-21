# Files Medias

The classic API and MAXON API provide tools and classes to handle file and media data. If possible, the classes of the MAXON API should be preferred.

Classic API:
- **c4d.bitmaps.BaseBitmap**: *The bitmap class can be used to load, read, draw and save bitmap pictures of various formats.*
- **c4d.storage.MultipassBitmap**: *An extension of the BaseBitmap class that supports higher bit depths, floating point images and multiple layers.*
- **c4d.storage.HyperFile**: *Hyper files are used to store data in a file. The HyperFile works with the `FIFO` concept. The values will be written and read in the same order.*
- **c4d.storage.MemoryFileStruct**: *Used to write to memory instead of to a file.*

Maxon API:
- **maxon.Url**: *Defines the location of a file or a similar resource*.
- **maxon.InputStream**: *An input stream is used to read data from a resource defined with a maxon::Url.*
- **maxon.OutputStream**: *An output stream is used to write data to a resource defined with a maxon::Url.*

## Examples

### copy_32bits_image
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Copies the internal data of a 32 bit per-channel image to a new one.

### export_alembic
Version: R14, R15, R16, R17, R18, R19, R20, R21, S22  - Win/Mac

    Exports Alembic with custom settings.

### export_obj
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Exports Obj with custom settings.
    
### geclipmap_fill_color_bitmap
Version: R18, R19, R20, R21, S22 - Win/Mac

    Adds an overlay color to a Picture.
    
### import_obj
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Imports Obj with custom settings.
    
### import_sketchup
Version: R17, R18, R19, R20, R21, S22 - Win/Mac

    Imports Sketchup File with custom settings.
    
### import_step
Version: R20, R21, S22 - Win/Mac

    Imports STP/STEP with custom settings.
    
### read_write_memory_file_bitmap
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Writes/Reads a bitmap to/from memory.

### read_write_memory_file_data
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22 - Win/Mac

    Writes/Reads simple data to/from memory.

### set_get_globaltexturepaths
Version: R20, R21, S22 - Win/Mac

    Sets and gets global texture paths (Preferences->Files->Paths).
