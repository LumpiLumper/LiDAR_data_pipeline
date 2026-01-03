
import os
import numpy as np
import laspy
from velodyne_decoder import read_pcap
from pathlib import Path

from pipeline.pcap_processer import PcapProcesser

# make folders for processed data ---------------------------------------------------------
print("creating folder structure...")
raw_dir = "raw_data"
train_dir = "training_data"
val_dir = "validation_data"
train_scene_path = Path(os.path.join(train_dir), "pcb_scene")
val_scene_path = Path(os.path.join(val_dir, "pcd_scene"))

split_ratio = 0.85

os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)
train_scene_path.mkdir(parents=True, exist_ok=True)
val_scene_path.mkdir(parents=True, exist_ok=True)

# !!!   important to check that there is no data in dirs
#       to not overwrite already labeled data
assert not any(f.endswith(".las") for f in os.listdir(train_dir)), \
        "train_data already contains .las files"

assert not any(f.endswith(".las") for f in os.listdir(val_dir)), \
        "validation_data already contains .las files"

# fetch pcap file from raw_data folder ---------------------------------------------------
pcap_files = [f for f in os.listdir(raw_dir) if f.endswith(".pcap")]
assert pcap_files, "No .pcap files found in raw_data"
assert len(pcap_files) == 1, "only one .pcap file in raw_data allowed"
pcap_file = os.path.join(raw_dir, pcap_files[0])

# get duration of scene ------------------------------------------------------------------
print("collecting timestamps...")
timestamps = []
for timestamp, cloud in read_pcap(pcap_file):
    time = timestamp.device
    timestamps.append(time)

t_start = timestamps[0]
t_end = timestamps[-1]
duration = t_end - t_start

cropped_clouds: list[np.ndarray] = []
pcap_processer = PcapProcesser()

progress_1 = 0

for frame_id, (timestamp, cloud) in enumerate(read_pcap(pcap_file)):
    cropped_clouds.append(pcap_processer.crop_cloud(cloud=cloud))
    time_passed = timestamp.device - t_start
    file_name = f"frame_{frame_id:05d}" # name will be frame_00000 | frame_00001 -> important so matlab labeler reads pcb scene in correct order
    if cropped_clouds[frame_id].shape[0] > 0:
        if time_passed <= duration * split_ratio:
            las_file = os.path.join(train_dir, f"{file_name}.las")
            pcd_file =  os.path.join(train_scene_path, f"{file_name}.pcd")
            las = pcap_processer.write_las(cropped_clouds[frame_id], time_passed + 1, las_file)
            pcap_processer.convert_las_to_pcd(las, pcd_file)
        else:
            las_file = os.path.join(val_dir, f"{file_name}.las")
            pcd_file = os.path.join(val_scene_path, f"{file_name}.pcd")
            las = pcap_processer.write_las(cropped_clouds[frame_id], time_passed + 1, las_file)
            pcap_processer.convert_las_to_pcd(las, pcd_file)
    else:
        print(f"frame {frame_id} is empty, no file generated")
    
    progress = round(time_passed / duration * 100)
    if progress > progress_1:
        print(f"file processing to las file: {progress}%")
        progress_1 = progress

print("Complete")