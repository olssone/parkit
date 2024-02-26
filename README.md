# Park It!
Parking Space Monitoring System for Senior Project. Spring 2024.

## Working on:
occupany+objectdetect-v2-working.py

## To run:
### Install Repo Dependencies
git clone https://github.com/olssone/parkit.git
cd parkit
python3 -m venv opencv-env
source opencv-env/bin/activate
pip install -r requirements.txt

### Install YOLOv5 Dependencies
```bash
git clone https://github.com/ultralytics/yolov5.git
```bash
cd yolov5
```bash
pip install -r requirements.txt

### Run the actual Parking Space Monitor Script
cd parkit/workingExamples/
python3 occupany+objectdetect-v2-working.py
