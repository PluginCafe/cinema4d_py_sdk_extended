"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Samples arbitrary points from multiple fields with c4d.FieldList and stores the result into a vertex color tag.

Class/method highlighted:
    - c4d.FieldList
    - c4d.modules.mograph.FieldLayer
    - c4d.modules.mograph.FieldInput
    - c4d.modules.mograph.FieldOutput

Compatible:
    - Win / Mac
    - R20, R21, S22
"""
import c4d


def main():
    # Checks if active object is valid
    if op is None:
        raise ValueError("op is none, please select one object.")

    # Checks if active object is a polygon object
    if not op.CheckType(c4d.Opolygon):
        raise TypeError("Selected object is not a polygon object.")

    # Retrieves the vertex color tag on the polygon object
    pointCount = op.GetPointCount()
    vertexColor = op.GetTag(c4d.Tvertexcolor)
    if not vertexColor:
        # Creates vertex color tag if it does not exist
        vertexColor = c4d.VertexColorTag(pointCount)
        if vertexColor is None:
            raise MemoryError("Failed to create a vertex color tag.")
        op.InsertTag(vertexColor)

    if vertexColor is None:
        RuntimeError("Failed to retrieve or create a vertex color tag.")

    # Creates linear field and adds it to the active document
    linearField = c4d.BaseObject(c4d.Flinear)
    if linearField is None:
        raise MemoryError("Failed to create a linear field.")

    doc.InsertObject(linearField)

    # Creates random field and adds it to the active document
    randomField = c4d.BaseObject(c4d.Frandom)
    if randomField is None:
        raise MemoryError("Failed to create a random field.")

    doc.InsertObject(randomField)

    # Creates layer for linear field and sets link
    linearFieldLayer = c4d.modules.mograph.FieldLayer(c4d.FLfield)
    if linearFieldLayer is None:
        raise MemoryError("Failed to create a field layer for linear field.")
    linearFieldLayer.SetLinkedObject(linearField)

    # Creates layer for random field and sets link
    randomFieldLayer = c4d.modules.mograph.FieldLayer(c4d.FLfield)
    if randomFieldLayer is None:
        raise MemoryError("Failed to create a field layer for random field.")
    randomFieldLayer.SetLinkedObject(randomField)

    # Creates a field list
    fields = c4d.FieldList()
    if fields is None:
        raise MemoryError("Failed to create a FieldList.")

    # Adds layers to the field list
    fields.InsertLayer(linearFieldLayer)
    fields.InsertLayer(randomFieldLayer)

    # Prepares field input with the points to sample
    inputField = c4d.modules.mograph.FieldInput(op.GetAllPoints(), pointCount)

    # Sample all the points of the polygon object
    output = fields.SampleListSimple(op, inputField, c4d.FIELDSAMPLE_FLAG_VALUE)

    # Writes field output values to the vertex color data
    writeData = vertexColor.GetDataAddressW()
    for pointIndex in range(pointCount):
        vertexColor.SetColor(writeData, None, None, pointIndex, c4d.Vector(output._value[pointIndex]))

    # Removes fields from the document
    linearField.Remove()
    randomField.Remove()

    # Pushes an update event to Cinema 4D
    c4d.EventAdd()


# Execute main()
if __name__ == '__main__':
    main()
