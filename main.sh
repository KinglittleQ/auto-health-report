#!/bin/bash
ROOT=$(pwd)

while true; do
  h=$(date +%H)
  if [ "$h" -eq "17" ]; then
    python3 $ROOT/main.py 
  fi
  sleep 1h
done