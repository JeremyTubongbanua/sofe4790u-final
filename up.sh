#!/bin/bash

FULL_PATH=$(realpath $0)
cd $(dirname $FULL_PATH)

tmux kill-session -t broker
tmux kill-session -t node0
tmux kill-session -t node1
tmux kill-session -t node2
tmux kill-session -t frontend

tmux new-session -d -s broker
tmux send-keys -t broker "cd broker" C-m
tmux send-keys -t broker "python3 node_server.py" C-m

sleep 1

tmux new-session -d -s node0
tmux send-keys -t node0 "cd node0" C-m
tmux send-keys -t node0 "python3 node_client.py --name node0" C-m

tmux new-session -d -s node1
tmux send-keys -t node1 "cd node1" C-m
tmux send-keys -t node1 "python3 node_client.py --name node1" C-m

tmux new-session -d -s node2
tmux send-keys -t node2 "cd node2" C-m
tmux send-keys -t node2 "python3 node_client.py --name node2" C-m

tmux new-session -d -s frontend
tmux send-keys -t frontend "cd frontend" C-m
tmux send-keys -t frontend "npm run dev --host" C-m

echo "http://192.168.8.125:5173/"

