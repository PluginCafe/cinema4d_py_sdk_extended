"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Distributes and creates Sphere along a Matrix Object with an InstanceObject.

Class/method highlighted:
    - c4d.InstanceObject
    - InstanceObject.SetReferenceObject()

"""
import c4d


def main():
    # Creates a matrix and a sphere object
    matrix = c4d.BaseObject(1018545)
    sphere = c4d.BaseObject(c4d.Osphere)

    # If the matrix or the sphere object is not created
    if matrix is None or sphere is None:
        raise RuntimeError("Failed to create a matrix object or a sphere.")

    # Inserts theses 2 objects in the current document.
    doc.InsertObject(matrix)
    doc.InsertObject(sphere)

    # Creates an instance object
    instance = c4d.InstanceObject()
    if instance is None:
        raise RuntimeError("Failed to create an instance object.")

    # Inserts the instance object in the active document
    doc.InsertObject(instance, None, None)

    # Defines the reference object to be instanced.
    instance.SetReferenceObject(sphere)

    # Defines the matrix object as input position object.
    instance[c4d.INSTANCEOBJECT_MULTIPOSITIONINPUT] = matrix
    instance[c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE] = c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE_MULTIINSTANCE

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


if __name__ == '__main__':
    main()
