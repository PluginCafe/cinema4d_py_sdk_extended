# Files Medias

The Cinema API and MAXON API provide tools and classes to handle file and media data. If possible, the classes of the MAXON API should be preferred.

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

    Copies the internal data of a 32 bit per-channel image to a new one.

### export_alembic

    Exports Alembic with custom settings.

### export_obj

    Exports Obj with custom settings.
    
### geclipmap_fill_color_bitmap

    Adds an overlay color to a Picture.
    
### import_obj

    Imports Obj with custom settings.
    
### import_sketchup

    Imports Sketchup File with custom settings.
    
### import_step

    Imports STP/STEP with custom settings.
    
### read_write_memory_file_bitmap

    Writes/Reads a bitmap to/from memory.

### read_write_memory_file_data

    Writes/Reads simple data to/from memory.

### set_get_globaltexturepaths

    Sets and gets global texture paths (Preferences->Files->Paths).
