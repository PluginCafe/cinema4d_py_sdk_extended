"""Demonstrates how to use KDTree to find neighboring points in a mesh.

This is an optimized version of the `kdtree_shortest_path.py` example that uses A* path finding and 
more efficient deduplication to handle larger meshes more quickly than the basic breadth-first search 
approach.
"""
__author__ = "Ferdinand Hoppe, Maxime Adam"
__copyright__ = "Copyright (C) 2026 MAXON Computer GmbH"
__date__ = "13/02/2026"
__license__ = "Apache-2.0 License"
__version__ = "2026.2.0"

import heapq

import c4d
import mxutils
import random

doc: c4d.documents.BaseDocument  # The currently active document.
op: c4d.BaseObject | None  # The primary selected object in `doc`. Can be `None`.

def FindShortestMeshPath(nbr: c4d.utils.Neighbor, points: list[c4d.Vector], 
                         start_idx: int, end_idx: int, 
                         neighbor_cache: dict, coordinates_cache: list) -> list[int] | None:
    """Finds the shortest path between two vertices in a mesh using optimized A* pathfinding.

    Uses A* algorithm with geometric heuristic for faster pathfinding compared to BFS.
    Includes neighbor caching to reduce expensive API calls.
    """
    if start_idx == end_idx:
        return [start_idx]
    
    # Cache target coordinates for heuristic calculations, and pre-compute the initial heuristic 
    # from start to target.
    target_x, target_y, target_z = coordinates_cache[end_idx]
    start_x, start_y, start_z = coordinates_cache[start_idx]
    dx, dy, dz = start_x - target_x, start_y - target_y, start_z - target_z
    initial_h: float = (dx*dx + dy*dy + dz*dz) * 0.01
    
    open_heap: list[tuple[float, float, int]] = [(initial_h, 0, start_idx)] # (f_score, g_score, vertex_id)
    open_dict: dict[int, float] = {start_idx: 0}  # vertex_id -> g_score
    closed_set: set[int] = set() # Set of vertex_ids that have been fully processed
    came_from: dict[int, int] = {} # vertex_id -> parent_vertex_id for path reconstruction
    
    # A* search loop
    while open_heap:
        # Get the vertex in the open set with the lowest f_score
        _, current_g, current = heapq.heappop(open_heap) 
        
        # Skip if already processed
        if current in closed_set:
            continue
        
        # Remove from open_dict since we're now processing it.
        open_dict.pop(current, None)
        closed_set.add(current)
        
        # If we reached the target, reconstruct the path and return it.
        if current == end_idx:
            path: list[int] = []
            while current != start_idx:
                path.append(current)
                current = came_from[current]
            path.append(start_idx)
            path.reverse()
            return path
        
        # Get neighbors using cache when available
        if current in neighbor_cache:
            neighbors: list[int] = neighbor_cache[current]
        else:
            neighbors: list[int] = nbr.GetPointOneRingPoints(current)
            neighbor_cache[current] = neighbors
        
        # Process each neighbor of the current vertex and update the open set accordingly.
        for neighbor in neighbors:
            if neighbor in closed_set:
                continue
                
            tentative_g = current_g + 1
            if neighbor not in open_dict or tentative_g < open_dict[neighbor]:
                came_from[neighbor] = current
                open_dict[neighbor] = tentative_g
                
                # Calculate heuristic to target
                neighbor_coords = coordinates_cache[neighbor]
                dx = neighbor_coords[0] - target_x
                dy = neighbor_coords[1] - target_y
                dz = neighbor_coords[2] - target_z
                h_score: float = (dx*dx + dy*dy + dz*dz) * 0.01
                
                f_score: float = tentative_g + h_score
                heapq.heappush(open_heap, (f_score, tentative_g, neighbor))
    
    return None

def deduplicate_segments(segments: list[list[c4d.Vector]]) -> list[list[c4d.Vector]]:
    """Removes duplicate path segments to clean up the visualization.
    
    Because we get all the n-units close points for each seed point, our paths often contain duplicates.
    This function uses coordinate hashing to efficiently identify and remove exact duplicate segments.
    """
    if not segments:
        return []
    
    seen = set()
    unique_segments = []
    
    for segment in segments:
        if segment:  # Skip empty segments
            # Create a unique identifier from the segment's coordinates rounded to 6 decimal places.
            # We use frozenset so that the hash is order-independent and consistent.
            coord_hash = hash(frozenset(
                (round(v.x, 6), round(v.y, 6), round(v.z, 6)) for v in segment
            ))
            
            if coord_hash not in seen:
                seen.add(coord_hash)
                unique_segments.append(segment)
    
    return unique_segments

def BuildOutput(seedPoints: list[c4d.Vector], neighborPoints: list[c4d.Vector], 
                pathSegments: list[list[c4d.Vector]], maxDimensions: float) -> None:
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
    
    def createInstance(obj: c4d.BaseObject, positions: list[c4d.Vector], color: c4d.Vector) -> c4d.BaseObject:
        instance: c4d.InstanceObject = mxutils.CheckType(c4d.BaseObject(c4d.Oinstance))
        instance[c4d.INSTANCEOBJECT_LINK] = obj
        instance[c4d.ID_BASEOBJECT_USECOLOR] = c4d.ID_BASEOBJECT_USECOLOR_ALWAYS
        instance[c4d.ID_BASEOBJECT_COLOR] = color
        instance[c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE] = c4d.INSTANCEOBJECT_RENDERINSTANCE_MODE_MULTIINSTANCE
        instance.SetInstanceMatrices([c4d.Matrix(pos) for pos in positions])
        return instance
    
    # Since this is a non-beginner example, we will not go into the details of building the output
    # objects, see one of the beginner examples for that.
    
    seedNull: c4d.BaseObject = mxutils.CheckType(c4d.BaseObject(c4d.Onull))
    seedNull.SetName("Seed Points")
    seedSphere: c4d.BaseObject = buildPoint(maxDimensions * 0.015)
    seedSphere.InsertUnder(seedNull)
    createInstance(seedSphere, seedPoints, c4d.Vector(1, 0, 0)).InsertUnder(seedNull)

    neighborNull: c4d.BaseObject = mxutils.CheckType(c4d.BaseObject(c4d.Onull))
    neighborNull.SetName("Neighbor Points")
    neighborSphere: c4d.BaseObject = buildPoint(maxDimensions * 0.01)
    neighborSphere.InsertUnder(neighborNull)
    createInstance(neighborSphere, neighborPoints, c4d.Vector(0, 1, 0)).InsertUnder(neighborNull)

    paths: c4d.SplineObject = mxutils.CheckType(c4d.SplineObject(0, c4d.SPLINETYPE_LINEAR))
    paths.SetName("Segment Paths")
    
    # Efficient list concatenation
    allPathPoints = []
    for segment in pathSegments:
        allPathPoints.extend(segment)
    
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
    
    This optimized version uses A* pathfinding and efficient deduplication to handle
    larger meshes more quickly than the basic breadth-first search approach.
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
    
    seedPointClusters: dict[int, list[int]] = {}
    for seedIdx in seedPointsIndices:
        cluster_data = kdData.FindRange(points[seedIdx], t, squared_distances=True)
        seedPointClusters[seedIdx] = cluster_data

    # Now that we have seed points and point clouds surrounding these seed points, we can start
    # building paths on the mesh from each seed point to its neighbors. To do that, we use an 
    # optimized A* algorithm on the mesh topology for faster pathfinding.

    # Instantiate a topology lookup helper for our object, which will allow us to easily get the 
    # neighbors of a vertex in the mesh.
    nbr: c4d.utils.Neighbor = c4d.utils.Neighbor()
    nbr.Init(op)

    # Pre-compute coordinate cache for faster heuristic calculations in A*
    coordinates_cache = [(point.x, point.y, point.z) for point in points]
    neighbor_cache = {}  # Cache neighbor lookups to reduce API calls
    
    # Build the segments connecting seed points to their neighbors.
    segments: list[list[c4d.Vector]] = []
    neighborPoints: set[c4d.Vector] = set()
    
    for seedIdx, clusterData in seedPointClusters.items():
        # The point ids of the neighboring points of #seedIdx and the actual neighboring points.
        # The latter are just later used for the visualization.
        neighborIds: list[int] = [n.get("node", {}).get("id", -1) for n in clusterData]
        neighborPoints.update(op.GetMg() * points[nid] for nid in neighborIds 
                              if nid != seedIdx)
        
        # Now we build the shortest path between the seed point and each of its neighbors using
        # an optimized A* algorithm. This is much faster than breadth-first search for larger meshes.
        for neighborIdx in neighborIds:
            if neighborIdx == seedIdx:
                continue

            path: list[int] | None = FindShortestMeshPath(
                nbr, points, seedIdx, neighborIdx, neighbor_cache, coordinates_cache
            )
            pathPoints: list[c4d.Vector] = [op.GetMg() * points[idx] 
                                            for idx in path] if path is not None else []
            segments.append(pathPoints)

    # Remove duplicate path segments using fast hash-based deduplication.
    # This is more efficient than subset checking for large numbers of segments.
    uniqueSegments = deduplicate_segments(segments)

    # And finally, we build the output objects to visualize the seed points, their neighbors and 
    # the paths between them.
    BuildOutput(seedPoints, list(neighborPoints), uniqueSegments, maxDimension)
    

if __name__ == '__main__':
    main()