"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam

Description:
    - Creates a Bitmap Loader to import a custom picture format into Cinema 4D.

Notes:
    - The Bitmap Exporter corresponding to the type can be found in the sdk under the py-xample_saver folder.
    - File format used is the next one:
        - 6 bits (XAMPLE identifier)
        - 24 bits (bit depth, width, height)
        - xx bits until en of file (bz2compressed each component 1 byte (red, green, blue))

Class/method highlighted:
    - c4d.plugins.BitmapLoaderData
    - BitmapLoaderData.Identify()
    - BitmapLoaderData.Load()

"""
import c4d
import struct
import bz2


# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1025255

BMP_NAME = "Py-XAMPLE Loader"
BMP_IDENTIFIER = b"XAMPLE"


class MyXampleLoader(c4d.plugins.BitmapLoaderData):
    """Data class to import a *.xample file"""

    def Identify(self, name, probe, size):
        """Called by Cinema 4D, to identifie your file type (know if this Bitmap Loader can be used with the current Bitmap).

        Args:
            name (str): The name of the file.
            probe (buffer): The start of data from the file currently tested.
            size (int): The size of the probe for testing this file type.

        Returns:
            True if the plugin can load this file.
        """
        # Checks if image starts with identifier flag
        return probe[:len(BMP_IDENTIFIER)] == BMP_IDENTIFIER
    
    def Load(self, name, bm, frame):
        """Called by Cinema 4D, when the plugin should loads the files as a BaseBitmap.

        Args:
            name (str): The name of the file.
            bm (c4d.bitmaps.BaseBitmap): The Bitmap, to be filled with the data (need to be initialized).
            frame (int): The current frame number for file format containing picture sequence (Quicktime, AVI...)

        Returns:
            IMAGERESULT
        """
        # Opens the file in binary read mode
        with open(name, "rb") as fn:
            # Skips identifier
            lines = fn.read()[len(BMP_IDENTIFIER):]

            # Calculates the bits size of 3 int and 3 char
            intBitsSize = struct.calcsize("iii")
            chatBitsSize = struct.calcsize("hhh")
            
            # Extracts bit depth, width and height information
            bt, width, height = struct.unpack("iii", lines[:intBitsSize])

            # Initialize the bitmap with the information provided
            if bm.Init(width, height, bt) != c4d.IMAGERESULT_OK:
                raise MemoryError("Failed to initialize the BaseBitmap.")

            # Removes the offset so we can start with position 0 of the pixel information
            lines = lines[intBitsSize:]

            # Decompress to raw data
            lines = bz2.decompress(lines)

            # Iterates each lines to fill the BaseBitmap
            for x in range(width):
                # Iterates each row
                for y in range(height):
                    # Retrieves memory position according current x and y pixels
                    fr = (y * width * chatBitsSize) + (x * chatBitsSize)

                    # Extracts red, green, blue information
                    r, g, b = struct.unpack("hhh", lines[fr:fr+chatBitsSize])

                    # Assigns pixel value for x, y pixel
                    bm[x, y] = r, g, b
        
        return c4d.IMAGERESULT_OK


if __name__ == "__main__":
    # Registers the bitmap loader plugin
    c4d.plugins.RegisterBitmapLoaderPlugin(id=PLUGIN_ID,
                                           str=BMP_NAME,
                                           info=0,
                                           dat=MyXampleLoader())
