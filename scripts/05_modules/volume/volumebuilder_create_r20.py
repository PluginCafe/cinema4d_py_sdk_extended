"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a volume builder and inserts it into the active document.

Class/method highlighted:
    - c4d.modules.volume.VolumeBuilder
    - BaseDocument.InsertObject()

"""
import c4d


def main():
    # Creates a volume builder object
    volumeBuilder = c4d.modules.volume.VolumeBuilder()
    if volumeBuilder is None:
        raise MemoryError("Failed to create a volume builder.")

    # Inserts it in the scene
    doc.InsertObject(volumeBuilder, None, None)

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
