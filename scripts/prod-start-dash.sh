#!/bin/sh
# Start dashboard stack on PROD
cd /home/sniegul/dashboard
# Start backend (port 8091)
python3 serve-dashboard.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 2
# Start forwarder (port 8090 -> 8091)
socat TCP-LISTEN:8090,fork,reuseaddr TCP:127.0.0.1:8091 &
FORWARD_PID=$!
echo "Forward PID: $FORWARD_PID"
echo "$BACKEND_PID $FORWARD_PID" > .dashboard_pids
