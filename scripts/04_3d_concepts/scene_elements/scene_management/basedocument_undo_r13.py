"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates two Undos steps (the user will have to press two times Undo to come back to the initial state of the scene).
    - In the first a null, a cube, a material, and a texture tag is created. Texture tag is created on the cube, and the material is assigned to it.
    - In the second, the texture tag is deleted and the cube is moved under the null.

Class/method highlighted:
    - BaseDocument.StartUndo()
    - BaseDocument.AddUndo()
    - BaseDocument.EndUndo()

"""
import c4d


def main():
    # Defines the initials state of the scene (the state that will be restored if the user do an "Undo")
    doc.StartUndo()

    # Creates few objects, tag, material to be inserted into the document later
    null = c4d.BaseObject(c4d.Onull)
    cube = c4d.BaseObject(c4d.Ocube)
    textureTag = c4d.BaseTag(c4d.Ttexture)
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    if null is None or cube is None or textureTag is None or mat is None:
        raise RuntimeError("Failed to create null or cube or textureTag or mat")

    # Inserts a Material into the active document
    doc.InsertMaterial(mat)
    doc.AddUndo(c4d.UNDOTYPE_NEW, mat)

    # Inserts both objects
    doc.InsertObject(null)
    doc.AddUndo(c4d.UNDOTYPE_NEW, null)

    # Inserts both objects
    doc.InsertObject(cube)
    doc.AddUndo(c4d.UNDOTYPE_NEW, cube)

    # Inserts the Texture Tag to the cube object
    cube.InsertTag(textureTag)
    doc.AddUndo(c4d.UNDOTYPE_NEW, textureTag)

    # Defines the material used in the Texture Tag to our material
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, textureTag)
    textureTag[c4d.TEXTURETAG_MATERIAL] = mat

    # Ends the first Undo step, so when the user will press Undo 1 time the document will be restored to this scene state.
    doc.EndUndo()

    # Defines another Undo step (so if the user want to go to the initial state he have to press Undo twice)
    doc.StartUndo()

    # Moves the cube object under the Null Object
    doc.AddUndo(c4d.UNDOTYPE_HIERARCHY_PSR, cube)
    cube.Remove()
    cube.InsertUnderLast(null)

    # Delete the Texture Tag
    doc.AddUndo(c4d.UNDOTYPE_DELETE, textureTag)
    textureTag.Remove()

    # Defines the final state of the scene
    doc.EndUndo()

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == "__main__":
    main()
