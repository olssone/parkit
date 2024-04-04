# Park It!
Parking Space Monitoring System for Senior Project. Spring 2024.

## To run:
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
### Run the actual Parking Space Monitor Script
```bash
cd parkit
python3 ParkitWatchDog.py
```
