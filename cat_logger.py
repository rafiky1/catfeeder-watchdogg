import cv2
import numpy as np
import time
import os
import requests
from datetime import datetime

SAVE_FOLDER = "snapshots"
CSV_FILE = "sessions.csv"
THRESHOLD = 500000  # Tune for sensitivity
INTERVAL = 5  # Seconds between frames
API_URL = "http://localhost:8000/log"

os.makedirs(SAVE_FOLDER, exist_ok=True)

def capture_frame():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SAVE_FOLDER}/frame_{timestamp}.jpg"
    os.system(f"libcamera-still -o {filename} --width 640 --height 480 --timeout 1")
    return filename

def detect_motion(prev_img, curr_img):
    diff = cv2.absdiff(prev_img, curr_img)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 25, 255, cv2.THRESH_BINARY)
    motion_score = np.sum(thresh)
    return motion_score > THRESHOLD

def log_session(start_time, duration, snapshot_path):
    with open(CSV_FILE, "a") as f:
        f.write(f"{start_time},{duration},{snapshot_path}\n")
    
    try:
        requests.post(API_URL, json={
            "timestamp": start_time,
            "duration": float(duration),
            "image": snapshot_path
        })
        print(f"[+] Logged session: {start_time} | {duration}s")
    except Exception as e:
        print(f"[!] Could not POST to API: {e}")

def main():
    print("[*] Starting CatFeeder Watchdog")
    prev_img = None
    eating = False
    start_time = None

    while True:
        filename = capture_frame()
        curr_img = cv2.imread(filename)

        if prev_img is not None:
            if detect_motion(prev_img, curr_img):
                if not eating:
                    eating = True
                    start_time = datetime.now()
                    print(f"[+] Eating started at {start_time}")
            else:
                if eating:
                    eating = False
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    log_session(start_time.isoformat(), duration, filename)
                    print(f"[-] Eating ended. Duration: {duration:.2f} seconds")

        prev_img = curr_img
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
