import numpy as np
import open3d as o3d
import matplotlib.cm as cm

class PcapProcesser:
    def __init__(self):
        self.x_lim = (0, 25)
        self.y_lim = (-8, 8)
        self.z_lim = (-0.5, 0.7)

    def crop_cloud(self, cloud):
        x, y, z = cloud[:, 0], cloud[:, 1], cloud[:, 2]

        mask = (
            (x >= self.x_lim[0]) & (x < self.x_lim[1]) &
            (y >= self.y_lim[0]) & (y < self.y_lim[1]) &
            (z >= self.z_lim[0]) & (z < self.z_lim[1])
        )
        return cloud[mask]
    
    def write_pcd(self, cloud, file):

        xyz = cloud[:,:3].astype(np.float32)


        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz)

        pcd.colors = o3d.utility.Vector3dVector(cloud[:, 3:6])

        # Write ASCII PCD (best for MATLAB)
        o3d.io.write_point_cloud(file, pcd, write_ascii=True)