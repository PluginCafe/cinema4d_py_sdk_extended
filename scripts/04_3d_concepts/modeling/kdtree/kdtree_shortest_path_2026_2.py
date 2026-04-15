"""Demonstrates how to use KDTree to find neighboring points in a mesh.

To run this example an editable polygon object must be selected. The script will randomly select 
seed points on that object, find their neighboring points using a KDTree, and then find the shortest 
path on the mesh between each seed point and its neighbors. Finally, it visualizes the seed points, 
their neighbors and the paths between them using simple geometry.

It also serves as a demonstrates the performance problems of using a KDTree in Python. Although 
KDTree allows very efficient neighbor lookups, the algorithms that often used in conjunction with 
KDTree do not perform well in Python, which can lead to long execution times for larger meshes.

Note:

    `kdtree_shortest_path_optimized.py` is an optimized version of this example that performances
    better by using more efficient algorithms for path finding and deduplication. But doing this,
    just writing more efficient algorithms, is not always possible, and heavy mesh processing in 
    Python will often be slow.
    
"""
__author__ = "Ferdinand Hoppe"
__copyright__ = "Copyright (C) 2026 MAXON Computer GmbH"
__date__ = "12/02/2026"
__license__ = "Apache-2.0 License"
__version__ = "2026.2.0"

import collections

import c4d
import mxutils
import random

doc: c4d.documents.BaseDocument  # The currently active document.
op: c4d.BaseObject | None  # The primary selected object in `doc`. Can be `None`.

def FindShortestMeshPath(nbr: c4d.utils.Neighbor, start_idx: int, end_idx: int) -> list[int] | None:
    """Finds the shortest path between two vertices in a mesh using breadth-first search.

    Not directly relevant for the KDTree example.
    """
    # First, we define the queue for BFS and a set to keep track of visited vertices, as well as a 
    # dictionary to keep track of the previous vertex for each visited vertex (so we can reconstruct 
    # the path later). Then we seed the BFS with the start vertex index.
    visited: set[int] = set()
    prev: dict[int, int] = {}
    queue: collections.deque[int] = collections.deque()
    queue.append(start_idx)
    visited.add(start_idx)

    # Now we loop until we either find the end vertex or exhaust all reachable vertices. In each
    # iteration, we pop a vertex index from the queue, check if it's the end vertex (meaning we've 
    # found the shortest path), and if not, we add all of its unvisited neighbors to the queue and 
    # mark them as visited.
    while queue:
        current: int = queue.popleft()

        # We found the end vertex, so we can reconstruct the path by backtracking through the `prev`
        # dictionary until we reach the start vertex (and with that construct the shortest path).
        if current == end_idx:
            path: list[int] = []
            while current != start_idx:
                path.append(current)
                current = prev[current]

            path.append(start_idx)
            path.reverse()
            return path
        
        # We are looking at all the direct neighbors of the current vertex. If we haven't visited a 
        # neighbor yet, we add it to the queue and mark it as visited.
        for neighbor in nbr.GetPointOneRingPoints(current):
            if neighbor not in visited:
                visited.add(neighbor)
                prev[neighbor] = current
                queue.append(neighbor)

    return None  # No path found

def BuildOutput(seedPoints: list[int], neighborPoints: list[int], pathSegments: list[list[c4d.Vector]],
                maxDimensions: float) -> None:
    """Builds the output objects (a spline for the paths, and spheres for the seed and neighbor points) 
    and inserts them into the document.

    Not directly relevant for the KDTree example.
    """
    def buildPoint(size: float) -> c4d.BaseObject:
        """Helper function to build a sphere object at the given position, with the given size and color.
        """
        point: c4d.BaseObject = mxutils.CheckType(c4d.BaseObject(c4d.Osphere))
        point[c4d.PRIM_SPHERE_SUB] = 4
        point[c4d.PRIM_SPHERE_RAD] = size
        return point
    
    def createInstance(obj: c4d.BaseObject, position: c4d.Vector, color: c4d.Vector) -> c4d.BaseObject:
        """Helper function to create an instance of the given object at the given position.

        We use instances to lessen a bit the impact of building all that data in the scene. The 
        cleaner approach would be to create a point object and then let MoGraph do the cloning onto 
        that point object. But for large object counts, we should never do build the same geometry 
        over and over again. Because although we do not do it ourself, Cinema 4D has still to build 
        500 sphere objects when we insert 500 sphere objects.

        Cinema 4D has a memoization system for objects, but that will only lessen the impact of 
        building the same geometry multiple times, it will never be as fast as use render instances 
        as we do here.
        """
        instance: c4d.BaseObject = mxutils.CheckType(c4d.BaseObject(c4d.Oinstance))
        instance[c4d.INSTANCEOBJECT_LINK] = obj
        instance[c4d.ID_BASEOBJECT_USECOLOR] = c4d.ID_BASEOBJECT_USECOLOR_ALWAYS
        instance[c4d.ID_BASEOBJECT_COLOR] = color
        instance[c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE] = c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE_SINGLEINSTANCE
        instance.SetAbsPos(position)
        return instance
    
    # Since this is a non-beginner example, we will not go into the details of building the output
    # objects, see one of the beginner examples for that. 
    
    seedNull: c4d.BaseObject = mxutils.CheckType(c4d.BaseObject(c4d.Onull))
    seedNull.SetName("Seed Points")
    seedSphere: c4d.BaseObject = buildPoint(maxDimensions * 0.015)
    seedSphere.InsertUnder(seedNull)
    for pnt in seedPoints:
        createInstance(seedSphere, pnt, c4d.Vector(1, 0, 0)).InsertUnder(seedNull)

    neighborNull: c4d.BaseObject = mxutils.CheckType(c4d.BaseObject(c4d.Onull))
    neighborNull.SetName("Neighbor Points")
    neighborSphere: c4d.BaseObject = buildPoint(maxDimensions * 0.01)
    neighborSphere.InsertUnder(neighborNull)
    for pnt in neighborPoints:
        createInstance(neighborSphere, pnt, c4d.Vector(0, 1, 0)).InsertUnder(neighborNull)

    paths: c4d.SplineObject = mxutils.CheckType(c4d.SplineObject(0, c4d.SPLINETYPE_LINEAR))
    paths.SetName("Segment Paths")
    allPathPoints: list[c4d.Vector] = sum(pathSegments, [])
    paths.ResizeObject(pcnt=len(allPathPoints), scnt=len(pathSegments))
    paths.SetAllPoints(allPathPoints)
    for i, segment in enumerate(pathSegments):
        paths.SetSegment(id=i, cnt=len(segment), closed=False)

    profile: c4d.SplineObject = mxutils.CheckType(c4d.BaseObject(c4d.Osplinecircle))
    profile[c4d.PRIM_CIRCLE_RADIUS] = maxDimensions * 0.0025
    profile[c4d.SPLINEOBJECT_SUB] = 1

    sweep: c4d.BaseObject = mxutils.CheckType(c4d.BaseObject(c4d.Osweep))
    sweep[c4d.ID_BASEOBJECT_USECOLOR] = c4d.ID_BASEOBJECT_USECOLOR_ALWAYS
    sweep[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(1, 1, 0)
    sweep.SetName("Path Sweep")
    paths.InsertUnder(sweep)
    profile.InsertUnder(sweep)

    root: c4d.BaseObject = mxutils.CheckType(c4d.BaseObject(c4d.Onull))
    root.SetName("KDTree Clustering Example")
    sweep.InsertUnder(root)
    neighborNull.InsertUnder(root)
    seedNull.InsertUnder(root)

    doc.StartUndo()
    doc.InsertObject(root)
    doc.AddUndo(c4d.UNDOTYPE_NEW, root)
    doc.EndUndo()
    c4d.EventAdd()

def main() -> None:
    """Called by Cinema 4D when the script is being executed.
    """
    if not isinstance(op, c4d.PolygonObject):
        c4d.gui.MessageDialog("Please select a polygon object and run the script again.")
        return
    
    # Seed the global random instance to the uuid of #op so that this script generates the same
    # seed points for the same object every time.
    random.seed(hash(op))
    
    # Get the points of the selected object.
    points: list[c4d.Vector] = op.GetAllPoints()
    pointCount: int = len(points)

    # Now we select 2% of our points as seed points for our clusters. We will find the neighbors of 
    # these seed points and then connect the seed points with their neighbors using a shortest path 
    # on the mesh (so that we get nice paths that follow the topology of the mesh).
    seedCount: int = max(2, int(pointCount * 0.02))
    seedPointsIndices: list[int] = random.choices(range(pointCount), k=seedCount)
    seedPoints: list[c4d.Vector] = [op.GetMg() * points[idx] for idx in seedPointsIndices]

    # Now we initialize a KDTree with the points of the object. A KDTree is a spatial data structure
    # that allows for efficient nearest neighbor searches.
    kdTree: c4d.utils.KDTree = c4d.utils.KDTree()
    kdTree.InsertFromPointObject(op)
    kdTree.Balance()
    kdData: c4d.utils.KDTreeQuery = kdTree.CreateQueryObject()

    # Now we find all points for each seed point that are within a certain radius. We use the 
    # bounding box of the object to determine the distance to be 2.5% of the longest side of the 
    # bounding box (0.05, i.e., 5% of the radius). We square that distance because as always,
    # squared distances are faster to compute than actual distances.
    bboxRadius: c4d.Vector = op.GetRad()
    maxDimension: float = max(bboxRadius.x, bboxRadius.y, bboxRadius.z)
    t: float = (maxDimension * 0.05) ** 2
    seedPointClusters: dict[int, list[int]] = {
        seedIdx: kdData.FindRange(points[seedIdx], t, squared_distances = True) 
        for seedIdx in seedPointsIndices
    }

    # Now that we have seed points and point clouds surrounding these seed points, we can start
    # building paths on the mesh from each seed point to its neighbors. To do that, we use a 
    # breadth-first search (BFS) algorithm on the mesh topology.

    # Instantiate a topology lookup helper for our object, which will allow us to easily get the 
    # neighbors of a vertex in the mesh.
    nbr: c4d.utils.Neighbor = c4d.utils.Neighbor()
    nbr.Init(op)

    # Build the segments connecting seed points to their neighbors.
    segments: list[list[c4d.Vector]] = []
    neighborPoints: set[c4d.Vector] = set()
    for seedIdx, clusterData in seedPointClusters.items():
        # The point ids of the neighboring points of #seedIdx and the actual neighboring points.
        # The latter are just later used for the visualization.
        neighborIds: list[int] = [n.get("node", {}).get("id", -1) for n in clusterData]
        neighborPoints.update(op.GetMg() * points[nid] for nid in neighborIds 
                              if nid != seedIdx)
        
        # Now we build the shortest path between the seed point and each of its neighbors. 
        # This is the most expensive part of the script, and demonstrates a fundamental problem
        # with KDTree in Python. The language Python is often not fast enough to make good use
        # of the high performance neighbor lookups that KDTree offers, as that often implies an
        # algorithmic complexity that does not perform well in Python.
        for neighborIdx in neighborIds:
            if neighborIdx == seedIdx:
                continue

            path: list[int] | None = FindShortestMeshPath(nbr, seedIdx, neighborIdx)
            pathPoints: list[c4d.Vector] = [op.GetMg() * points[idx] 
                                            for idx in path] if path is not None else []
            segments.append(pathPoints)

    # Because we got all the n-units close points for each seed point, the chances are hight that 
    # our paths contain duplicates. So, we remove all paths that appear as a subset in other paths. 
    # This is only a cheap way to do this, for complex meshes we would have to do better cleanups of 
    # our segments, as this simple cleanup will still leave a lot of duplicate data in there.
    uniqueSegments: list[list[c4d.Vector]] = []
    for segment in segments:
        if not any(set(segment).issubset(set(other)) for other in segments if other != segment):
            uniqueSegments.append(segment)

    # And finally, we build the output objects to visualize the seed points, their neighbors and 
    # the paths between them.
    BuildOutput(seedPoints, list(neighborPoints), uniqueSegments, maxDimension)
    

if __name__ == '__main__':
    main()