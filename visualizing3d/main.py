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

# --- Step 5: Vertical plane aligned with Step 6 cut ---
bbox = mesh_crop.get_axis_aligned_bounding_box()
min_bound = bbox.min_bound
max_bound = bbox.max_bound
width = max_bound[0] - min_bound[0]
depth = max_bound[1] - min_bound[1]
height = max_bound[2] - min_bound[2]

# We'll cut vertically along the X axis (middle of model)
x0 = np.median(np.asarray(mesh_crop.vertices)[:, 0])

# Create thin vertical box (plane)
plane = o3d.geometry.TriangleMesh.create_box(
    width=0.01,                # very thin → plane-like
    height=height * 5,       # tall enough to cover full model
    depth=depth * 0.8          # wide enough to span across model
)
plane.paint_uniform_color([0.3, 0.3, 0.3])

# Move plane to center (x0) and align bottom with model base
plane.translate([
    x0 - 0.005,                # plane thickness offset
    min_bound[1] - 0.1 * depth,
    min_bound[2] - 0.1 * height
])

print("\nSTEP 5: Vertical Plane + Mesh (aligned for vertical cut)")
print("Plane X position (x0):", x0)
o3d.visualization.draw_geometries([mesh_crop, plane], window_name="STEP 5")


# --- Step 6: Clipping (vertical cut along X axis) ---
x_values = np.asarray(mesh_crop.vertices)[:, 0]
x0 = np.median(x_values)
idx = np.where(x_values > x0)[0].tolist()  # keep right side of model
clipped_mesh = mesh_crop.select_by_index(idx)

print("\nSTEP 6: Clipped Mesh (vertical cut)")
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
