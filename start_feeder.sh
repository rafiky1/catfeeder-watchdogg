#!/bin/bash
cd /home/dsc333/streetlens-lite
source env/bin/activate

# Start background processes
nohup uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload > fastapi.log 2>&1 &
sleep 5
nohup streamlit run dashboard.py --server.address=0.0.0.0 > streamlit.log 2>&1 &
nohup python camera_logger.py > logger.log 2>&1 &

# Wait forever so systemd doesn't restart the service
tail -f /dev/null
