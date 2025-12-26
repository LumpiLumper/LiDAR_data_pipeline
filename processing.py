"""
run with:
python3 -m processing
"""

import os
from velodyne_decoder import read_pcap
import open3d as o3d
import numpy as np
from pcap_processer import PcapProcesser


# make folders for processed data ---------------------------------------------------------
raw_dir = "raw_data"
train_dir = "training_data"
val_dir = "validation_data"

split_ratio = 0.85

os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)

# !!!   important to check that there is no data in dirs
#       to not overwrite already labeled data
assert not any(f.endswith(".pcap") for f in os.listdir(train_dir)), \
        "train_data already contains .pcap files"

assert not any(f.endswith(".pcap") for f in os.listdir(val_dir)), \
        "validation_data already contains .pcap files"

# fetch pcap file from raw_data folder ---------------------------------------------------
pcap_files = [f for f in os.listdir(raw_dir) if f.endswith(".pcap")]
assert pcap_files, "No .pcap files found in raw_data"
assert len(pcap_files) == 1, "only one .pcap file in raw_data allowed"
pcap_file = os.path.join(raw_dir, pcap_files[0])

# get duration of scene ------------------------------------------------------------------
timestamps = []
for timestamp, cloud in read_pcap(pcap_file):
    time = timestamp.device
    timestamps.append(time)

t_start = timestamps[0]
t_end = timestamps[-1]
duration = t_end - t_start

# crop frames and save as pcd file ------------------------------------------------------
processed_clouds: list[np.ndarray] = []
pcap_processer = PcapProcesser()

progress_1 = 0
for frame_id, (timestamp, cloud) in enumerate(read_pcap(pcap_file)):
    cropped_cloud = pcap_processer.crop_cloud(cloud=cloud)
    processed_clouds.append(cropped_cloud)
    time_passed = timestamps[frame_id] - t_start
    file_name = f"Frame {frame_id}.pcd"
    if time_passed < duration * split_ratio:
        file = os.path.join(train_dir, file_name)
        pcap_processer.write_pcd(cloud, file)
    else:
        file = os.path.join(val_dir, file_name)
        pcap_processer.write_pcd(cloud, file)
    
    progress = round(time_passed / duration * 100)
    if progress_1 < progress:
        print(f"File processing progress: {progress}%")
        progress_1 = progress