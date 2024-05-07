# Park It!
Parking Space Monitoring System for Hood College CS Senior Project. Spring 2024.

Software Project by Elijah Olsson, Subhashree Susindran, and Jake Wantz.

[Link text](https://github.com/olssone/parkit)

## Installation:
Enter all the commands in order, one at a time!
### Install Repo Dependencies
```bash
git clone https://github.com/olssone/parkit.git
cd parkit
python3 -m venv opencv-env
source opencv-env/bin/activate
pip install -r requirements.txt
```
### Install YOLOv5 Dependencies
```bash
git clone https://github.com/ultralytics/yolov5.git
cd yolov5
pip install -r requirements.txt
```
### Run the "Park-It!" system:
```bash
cd parkit
./RunParkit
```
