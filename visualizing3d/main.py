import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
import os

# File path
# path = "C:/projects/valorant_tournament_data_analytics/visualizing3d/Model/eyeball.ply" # Eyeball

path = "C:/projects/valorant_tournament_data_analytics/visualizing3d/cyber-samurai/source/RoninFinalS/RoninFinalS.obj" # Samurai

if not os.path.exists(path):
    print("❌ File not found. Check the path!")
    exit()

# --- Step 1: Load and show mesh ---
mesh = o3d.io.read_triangle_mesh(path)
mesh.compute_vertex_normals()

print("\nSTEP 1: Original Mesh")
print("Vertices:", len(mesh.vertices))
print("Triangles:", len(mesh.triangles))
print("Has colors:", mesh.has_vertex_colors())
print("Has normals:", mesh.has_vertex_normals())
o3d.visualization.draw_geometries([mesh], window_name="STEP 1")

# --- Step 2: Convert to point cloud ---
pcd = mesh.sample_points_uniformly(number_of_points=50000)
print("\nSTEP 2: Point Cloud")
print("Points:", len(pcd.points))
print("Has colors:", pcd.has_colors())
o3d.visualization.draw_geometries([pcd], window_name="STEP 2")

# --- Step 3: Poisson reconstruction ---
mesh_poisson, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8)
bbox = mesh.get_axis_aligned_bounding_box()
mesh_crop = mesh_poisson.crop(bbox)

print("\nSTEP 3: Reconstructed Mesh")
print("Vertices:", len(mesh_crop.vertices))
print("Triangles:", len(mesh_crop.triangles))
print("Has colors:", mesh_crop.has_vertex_colors())
o3d.visualization.draw_geometries([mesh_crop], window_name="STEP 3")

# --- Step 4: Voxelization ---
voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size=0.05)
print("\nSTEP 4: Voxelization")
print("Voxels:", len(voxel_grid.get_voxels()))
print("Has colors:", pcd.has_colors())  # voxel grid itself has no color attr
o3d.visualization.draw_geometries([voxel_grid], window_name="STEP 4")

# --- Step 5: Add plane ---
# --- Step 5: Add ground plane (aligned to model base) ---
# Get model bounds
bbox = mesh_crop.get_axis_aligned_bounding_box()
min_bound = bbox.min_bound
max_bound = bbox.max_bound

# Compute width (x) and depth (y)
width = max_bound[0] - min_bound[0]
depth = max_bound[1] - min_bound[1]
bottom_z = min_bound[2]

# Create plane slightly larger than model
plane = o3d.geometry.TriangleMesh.create_box(
    width=width * 1.2, height=0.01, depth=depth * 1.2
)
plane.paint_uniform_color([0.3, 0.3, 0.3])

# Center plane under model
plane.translate([
    min_bound[0] - 0.1 * width,    # shift X
    min_bound[1] - 0.1 * depth,    # shift Y
    bottom_z - 0.01                # shift Z just below base
])

print("\nSTEP 5: Plane + Mesh (aligned to base)")
o3d.visualization.draw_geometries([mesh_crop, plane], window_name="STEP 5")


# --- Step 6: Clipping (cut by median Z) ---
z_values = np.asarray(mesh_crop.vertices)[:, 2]
z0 = np.median(z_values)
idx = np.where(z_values > z0)[0].tolist()
clipped_mesh = mesh_crop.select_by_index(idx)

print("\nSTEP 6: Clipped Mesh")
print("Remaining vertices:", len(idx))
print("Triangles:", len(clipped_mesh.triangles))
print("Has colors:", clipped_mesh.has_vertex_colors())
print("Has normals:", clipped_mesh.has_vertex_normals())
o3d.visualization.draw_geometries([clipped_mesh], window_name="STEP 6")

# --- Step 7: Color gradient + extreme points ---
points = np.asarray(mesh_crop.vertices)
z_min, z_max = points[:, 2].min(), points[:, 2].max()
norm_z = (points[:, 2] - z_min) / (z_max - z_min)
mesh_crop.vertex_colors = o3d.utility.Vector3dVector(plt.cm.coolwarm(norm_z)[:, :3])

min_p = points[np.argmin(points[:, 2])]
max_p = points[np.argmax(points[:, 2])]

sphere_min = o3d.geometry.TriangleMesh.create_sphere(radius=0.05)
sphere_min.translate(min_p)
sphere_min.paint_uniform_color([1, 0, 0])  # red = min

sphere_max = o3d.geometry.TriangleMesh.create_sphere(radius=0.05)
sphere_max.translate(max_p)
sphere_max.paint_uniform_color([0, 0, 1])  # blue = max

print("\nSTEP 7: Gradient + Extremes")
print("Z min:", min_p)
print("Z max:", max_p)
o3d.visualization.draw_geometries([mesh_crop, sphere_min, sphere_max], window_name="STEP 7")
