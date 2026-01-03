import numpy as np
import laspy
from pyproj import CRS
import matplotlib.pyplot as plt
import open3d as o3d



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
    
    def write_las(self, cloud, time, file):
        assert time > 0, "time expected to be positive"

        header = laspy.LasHeader(point_format=1, version="1.2")
        header.scales = np.array([0.01, 0.01, 0.01])
        header.offsets = np.array([0.0, 0.0, 0.0])
        #header.add_crs(CRS.from_epsg(32632))

        las = laspy.LasData(header)

        las.x = cloud[:, 0]
        las.y = cloud[:, 1]
        las.z = cloud[:, 2]
        intensity = cloud[:, 3]
        intensity = np.nan_to_num(intensity)
        intensity = np.clip(intensity, 0, 65535)
        intensity = intensity.astype(np.uint16) # important for matlab lidar labeler, must be uint16!!
        las.intensity = intensity
        las.gps_time = np.full(len(las.x), time).astype(np.float64) # every point needs timestamp
        las.classification = np.ones(len(las.x), dtype=np.uint8)
        las.return_number = np.ones(len(las.x), dtype=np.uint8)
        las.number_of_returns = np.ones(len(las.x), dtype=np.uint8)
        las.scan_angle_rank = np.zeros(len(las.x), dtype=np.int8) # important for matlab lidar labeler
        las.write(file)
        return las

    def convert_las_to_pcd(self, las, output_filename, gamma=0.7):
        points = np.vstack((las.x, las.y, las.z)).transpose()
        
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)

        if hasattr(las, 'intensity'):
            rgb_colors = self.get_rgb_intensity_colors(las.intensity, 'viridis')
            pcd.colors = o3d.utility.Vector3dVector(rgb_colors.astype(np.float64))
        else:
            print(f"no intensity found in las file for {output_filename}")

        # 4. Write to disk
        o3d.io.write_point_cloud(output_filename, pcd)

    def get_rgb_intensity_colors(self, intensity_array, cmap_name='viridis'):
        # 1. Convert to float32
        raw = intensity_array.astype(np.float32)
        
        # 2. Robust Normalization (Stretching the 3-175 range)
        v_min, v_max = np.percentile(raw, [2, 98])
        if v_max <= v_min:
            return np.zeros((len(raw), 3))
        
        normalized = np.clip((raw - v_min) / (v_max - v_min), 0, 1)
        
        # 3. Apply Gamma to make mid-tones more vibrant
        gamma_corrected = np.power(normalized, 0.5)
        
        # 4. Apply the Colormap
        # 'viridis' is great for visibility; 'jet' is the classic blue-to-red
        colormap = plt.get_cmap(cmap_name)
        
        # This returns an (N, 4) array (RGBA). We only need the first 3 (RGB).
        colors_rgba = colormap(gamma_corrected)
        rgb_colors = colors_rgba[:, :3] 
        
        return rgb_colors