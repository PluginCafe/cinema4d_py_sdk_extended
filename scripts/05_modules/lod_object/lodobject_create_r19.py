"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Creates a new LOD object and adds it to the active BaseDocument.

Class/method highlighted:
    - c4d.LodObject
    - BaseDocument.InsertObject()

"""
import c4d


lodObject = c4d.LodObject()
lodObject.SetName("New LOD Object")
doc.InsertObject(lodObject)
c4d.EventAdd()
