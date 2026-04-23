#coding: utf-8
"""Demonstrates how to execute the 'Bridge' tool.

Invokes 'Bridge' in two different ways: first with distinct elements, then with selection islands.
Best used with the example scene of the same name in this folder.

Note:
    This example assumes the user is already familiar with modeling commands in general, and explores
    a more complex command in detail: the Bridge tool.
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2022 MAXON Computer GmbH"
__date__ = "23/04/2026"
__license__ = "Apache-2.0 License"
__version__ = "2026.2"

import c4d
import mxutils 

doc: c4d.documents.BaseDocument # The active document.
op: c4d.BaseObject | None # The active object, or None if no object is active.

def CopyObjects(items: list[c4d.BaseObject]) -> tuple[c4d.BaseObject, ...]:
    """Copies the given objects, renames them, moves them aside, and inserts them into the document.

    This is a helper function not directly related to the topic of this example.
    """
    copies: list[c4d.BaseObject] = []
    for item in items:
        copy: c4d.BaseObject = mxutils.CheckType(item.GetClone())
        copy.SetName(item.GetName() + "_Copy")
        radius: c4d.Vector = copy.GetRad()
        copy.SetMg(copy.GetMg() * c4d.utils.MatrixMove(c4d.Vector(0, radius.y * 3, 0)))
        doc.InsertObject(copy)
        doc.AddUndo(c4d.UNDOTYPE_NEW, copy)
        copies.append(copy)
    return tuple(copies)

def main() -> None:
    """Runs the example.
    """
    # Get the selected objects. We need exactly two polygon objects for this example.
    selObjects: list[c4d.BaseObject] = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_NONE)
    if len(selObjects) != 2 or not all(isinstance(obj, c4d.PolygonObject) for obj in selObjects):
        return c4d.gui.MessageDialog("Please select exactly two polygon objects.")
    
    objA: c4d.PolygonObject = selObjects[0]
    objB: c4d.PolygonObject = selObjects[1]

    # Get the polygon and point selections of the two objects and convert them into indices. 
    # Selections are stored as a list of Booleans in Cinema 4D. E.g., an object with 4 points and 
    # the first and last point being selected would have a selection of [True, False, False, True]. 
    # Often we have to convert such data into the indices of selected elements, e.g., [0, 3] in the 
    # previous example. We do this with a list comprehension that enumerates the selection and 
    # collects the indices of selected elements.
    pointSelectionA: c4d.BaseSelect = objA.GetPointS()
    pointSelectionB: c4d.BaseSelect = objB.GetPointS()
    polySelectionA: c4d.BaseSelect = objA.GetPolygonS()
    polySelectionB: c4d.BaseSelect = objB.GetPolygonS()

    # Convert the BaseSelect into indices of selected elements.
    selPointIndicesA: list[int] = [
        i for i, s in enumerate(pointSelectionA.GetAll(objA.GetPointCount())) if s]
    selPointIndicesB: list[int] = [
        i for i, s in enumerate(pointSelectionB.GetAll(objB.GetPointCount())) if s]
    selPolyIndicesA: list[int] = [
        i for i, s in enumerate(polySelectionA.GetAll(objA.GetPolygonCount())) if s]
    selPolyIndicesB: list[int] = [
        i for i, s in enumerate(polySelectionB.GetAll(objB.GetPolygonCount())) if s]
    
    if not len(selPointIndicesA) == len(selPointIndicesB) == 1:
        return c4d.gui.MessageDialog("Please select exactly one point in each object.")
    if len(selPolyIndicesA) < 1 or len(selPolyIndicesB) < 1:
        return c4d.gui.MessageDialog("Please select at least one polygon in each object.")
    
    selPointIndexA: int = selPointIndicesA[0]
    selPointIndexB: int = selPointIndicesB[0]

    # When we bridge an object, we have many settings as defined in toolbridge.h, and we have the 
    # usual decision of operating in point, edge, or polygon mode for a tool. But the Bridge tool 
    # also has another distinction in how it operates. We can bridge distinct 
    # elements in one or many objects, or we can bridge selection islands. Let's split this into two examples.

    # --- SIMPLE CASE: BRIDGING DISTINCT ELEMENTS --------------------------------------------------

    # This case is relatively simple. We have distinct elements in one or many input objects:
    #
    #   - Point Mode: 4 points in 1-4 objects
    #   - Edge Mode: 2 edges in 1-2 objects
    #   - Polygon Mode: 2 polygons in 1-2 objects

    # We draw two copies of the objects we want to bridge, so that we can run two examples. Since
    # we already add objects (modify the document), we start our undo step here.
    doc.StartUndo()
    objACopy, objBCopy = CopyObjects([objA, objB])

    # Now we set up our data. First, we must describe the objects we want to bridge. If we had 
    # more objects (in point mode), we would also have to set MDATA_BRIDGE_OBJINDEX3 and 
    # MDATA_BRIDGE_OBJINDEX4. When we have fewer objects than the mode supports, we just set the same 
    # objects multiple times.
    settings: c4d.BaseContainer = c4d.BaseContainer()
    settings[c4d.MDATA_BRIDGE_OBJINDEX1] = objACopy
    settings[c4d.MDATA_BRIDGE_OBJINDEX2] = objBCopy

    # Now we set the indices of the elements we want to bridge. The meaning is derived from
    # the MODELINGCOMMANDMODE we specify when executing the command. We will use polygon mode, so
    # the indices we specify will be interpreted as polygon indices in relation to the objects we 
    # specified above. We just pick the first selected polygon of each object; there is no guarantee
    # that this will result in a meaningful bridge. Figuring this out programmatically (which 
    # polygons 'line up' with each other) is not trivial and realistically requires some user input
    # for meaningful results.
    settings[c4d.MDATA_BRIDGE_ELEMENT1] = selPolyIndicesA[0]
    settings[c4d.MDATA_BRIDGE_ELEMENT2] = selPolyIndicesB[0]

    # Now we carry out the command. Since we will modify the objects in the document, we also add
    # undo steps for them. We could also use the flag MODELINGCOMMANDFLAGS_CREATEUNDO, but it can
    # be a bit unreliable, so I prefer to add the undo steps myself.
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, objACopy)
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, objBCopy)
    if not c4d.utils.SendModelingCommand(command=c4d.ID_MODELING_BRIDGE_TOOL,
                                         list=[objACopy, objBCopy],
                                         mode=c4d.MODELINGCOMMANDMODE_POLYGONSELECTION,
                                         bc=settings,
                                         doc=doc):
        doc.EndUndo()
        doc.DoUndo()
        return c4d.gui.MessageDialog("Bridge command failed.")

    # --- ADVANCED CASE: BRIDGING ISLANDS ----------------------------------------------------------

    # In this case, we do not bridge distinct elements, but instead bridge whole selection islands. This
    # only works in edge and polygon mode. This largely works the same but has some differences:
    #
    #   - Since this is only possible in edge and polygon mode, we can have at most two input objects.
    #   - This always requires at least one selection island in each input object (and for a single 
    #     object two selections) that matches the operation mode we are in (in our case a polygon 
    #     selection).
    #   - There is a special syntax as how to specify the element indices.

    # We again define the object(s) we want to bridge.
    settings: c4d.BaseContainer = c4d.BaseContainer()
    settings[c4d.MDATA_BRIDGE_OBJINDEX1] = objA
    settings[c4d.MDATA_BRIDGE_OBJINDEX2] = objB

    # Now we have to specify one polygon in the active selection of each object that belongs to 
    # the island we want to bridge. The tool will then 'grow' out from these polygons to find the 
    # whole island, and then bridge the two islands. We again just pick the first element of our
    # selections, but we will overwrite this here in second case below to make a better choice.
    settings[c4d.MDATA_BRIDGE_ELEMENT1] = selPolyIndicesA[0]
    settings[c4d.MDATA_BRIDGE_ELEMENT2] = selPolyIndicesB[0]

    # But even though we only have two input objects, we here also have to specify elements
    # 3 and 4. We have to fill them with the starting and end point of the bridge input (what the 
    # user would pick in the editor). These points must lie within the edges or polygons we specified 
    # for MDATA_BRIDGE_ELEMENT1 and MDATA_BRIDGE_ELEMENT2. 
    # 
    # Here I show two ways to do this: randomly pick a point derived from the polygon indices (not 
    # recommended), or use a user-provided point selection to guide us (already prepared above).

    # Option 1: Just pick a random point from the more or less randomly selected polygons from the 
    # islands (we just picked the first polygon). This is very likely to yield undesirable results,
    # as the points and polygons we pick 'line up' with each other.
    polyA: c4d.CPolygon = objA.GetPolygon(selPolyIndicesA[0])
    polyB: c4d.CPolygon = objB.GetPolygon(selPolyIndicesB[0])
    p: int = polyA.a
    q: int = polyB.a

    # Option 2: Instead, we use a user provided point selection and derive from that the polygons that
    # must be the starting and end polygons.

    # Get all polygons of both objects.
    polygonsA: list[c4d.CPolygon] = objA.GetAllPolygons()
    polygonsB: list[c4d.CPolygon] = objB.GetAllPolygons()
    
    # Find the polygon of #A in its active polygon selection that contains the selected point in #A.
    startPolygonIndexA: int | None = next(
        # For each index #i and polygon #poly in #objA (next() will return the first match)
        (i for i, poly in enumerate(objA.GetAllPolygons())
         # Include #i if it is in the selected polygon indices and if the selected point is part of 
         # that polygon #poly.
         if i in selPolyIndicesA and selPointIndexA in (poly.a, poly.b, poly.c, poly.d)),
        # Otherwise, returns None.
        None)
    
    # Repeat for object #B and its selected point and polygon selection.
    endPolygonIndexB: int | None = next(
        (i for i, poly in enumerate(objB.GetAllPolygons()) 
         if i in selPolyIndicesB and selPointIndexB in (poly.a, poly.b, poly.c, poly.d)), 
         None)
    
    if startPolygonIndexA is None or endPolygonIndexB is None:
        doc.EndUndo()
        doc.DoUndo()
        return c4d.gui.MessageDialog("Please select points that lie within the selected polygons.")

    # Now we assign the polygon and point indices to the settings.
    settings[c4d.MDATA_BRIDGE_ELEMENT1] = startPolygonIndexA
    settings[c4d.MDATA_BRIDGE_ELEMENT2] = endPolygonIndexB
    settings[c4d.MDATA_BRIDGE_ELEMENT3] = selPointIndexA
    settings[c4d.MDATA_BRIDGE_ELEMENT4] = selPointIndexB

    # We must also set these two fields to enable island growing behavior.
    settings.SetBool(c4d.MDATA_BRIDGE_FIRST_SELECT_ONLY, True)
    settings.SetBool(c4d.MDATA_BRIDGE_SECOND_SELECT_ONLY, True)

    # Now we carry out the command.
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, objA)
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, objB)
    if not c4d.utils.SendModelingCommand(command=c4d.ID_MODELING_BRIDGE_TOOL,
                                         list=[objA, objB],
                                         mode=c4d.MODELINGCOMMANDMODE_POLYGONSELECTION,
                                         bc=settings,
                                         doc=doc):
        doc.EndUndo()
        doc.DoUndo()
        return c4d.gui.MessageDialog("Bridge command failed.")
    
    # Finally, we end our undo step and inform Cinema 4D that the document has been modified.
    doc.EndUndo()
    c4d.EventAdd()


# Run it
if __name__ == '__main__':
    main()