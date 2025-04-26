🐾 CatFeeder Watchdog

A lightweight Raspberry Pi-powered system to monitor, track, and analyze your cat's feeding behavior — in real-time!
Built with Python, Streamlit, FastAPI, and SQLite3.

📸 Features

🔔 Alerts if your cat hasn't eaten in a set number of hours
📈 Feeding Activity Trend (total sessions and average duration)
⏳ Meal Duration Categories (short, medium, long)
🕒 Feeding Time-of-Day Analysis (feeding pattern by hours)
📷 Recent Snapshots captured during feeding
🐍 Auto-start on Raspberry Pi boot

📊 Dashboard Preview


🚀 How to Run

Clone this repo:
git clone https://github.com/rafiky1/catfeeder-watchdogg.git
cd catfeeder-watchdogg
Install the dependencies:
pip install -r requirements.txt
Run the API server:
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
Run the Dashboard:
streamlit run dashboard.py
(Optional) Auto-start on Raspberry Pi boot:
Configure the start_feeder.sh script with systemd
Your server and dashboard will auto-launch at startup!

🛠 Technologies Used

Python 3.11
Streamlit – Dashboard interface
FastAPI – REST API backend
SQLite3 – Lightweight database
Raspberry Pi – Hardware controller
Ngrok – Secure public access to dashboard (optional)

📁 Project Structure

catfeeder-watchdogg/
├── api_server.py
├── dashboard.py
├── detections.db
├── start_feeder.sh
├── requirements.txt
├── README.md
├── sessions.csv
└── snapshots/

Author
GitHub: rafiky1

