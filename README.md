# LiDAR Data Pipeline

This Python script converts LiDAR data recordings form a VLP-16 saved as pcap files
and processes it's clouds fit for use in FS-Driverless object identification, labeling with MatLab Lidar Labeler, path planning and SLAM application.

## Project Structure
* `pipeline/` - Core Python scripts for processing PCAP to training and validation data. LAS clouds with raw intensity and timestamps and PCD scene ready for labeling in MatLab Labeler.
* `raw/` - Directory for input .pcap files.
* `training_data/` - Pipeline creats this folder containing all LAS files before datasplit (see pipeline.py; default datasplit is 85%) and a subfolder "pcd_scene" that can be used in MatLab Lidar Labeler.
* `val_data/` - Analog to "training_data"
* `requirements.txt` - Python dependencies list.

---

## Setup Instructions

### 1. Clone the Repository
run this in terminal:
git clone [https://github.com/LumpiLumper/LiDAR_data_pipeline.git](https://github.com/LumpiLumper/LiDAR_data_pipeline.git)
cd LiDAR_data_pipeline

### 2. Setup virtual machine

To ensure portability across different operating systems, we use a Virtual Environment.

Windows:
run the following commands in PowerShell inside your data folder (...\create_training_data):
python -m venv .venv    
.\.venv\Scripts\Activate.ps1

Linux/Mac:
run the following commands in terminal inside your data folder (.../create_training_data)
python3 -m venv .venv
source .venv/bin/activate

Once the environment is active, install the required libraries:
pip install -r requirements.txt