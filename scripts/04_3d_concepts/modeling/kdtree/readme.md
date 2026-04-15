# kdtree_lookup_shortest_path_on_mesh_2026_2.py

Demonstrates how to use KDTree to find neighboring points in a mesh.

In this example we select a polygon object, randomly select some seed points on that object, find the
neighboring points of those seed points using a KDTree, and then find the shortest path on the mesh
between each seed point and its neighbors. Finally, we visualize the seed points, their neighbors and
the paths between them using some simple geometry.

This example also serves as a demonstration of the problem of using KDTree in Python. Although 
KDTree allows us to do very efficient neighbor lookups, the algorithms that we often want to use 
together with these neighbor lookups often have a complexity that does not perform well in Python.

![](shortest_path_preview.png)