#!/bin/bash

# Deploy script, called by GitHub webhook

LOG_FILE=deploy.log

echo "Deploying at $(date)" >> $LOG_FILE 
git pull 2>> $LOG_FILE
pip install -r requirements.txt 2>> $LOG_FILE
systemctl restart tuppence.service 2>> $LOG_FILE
echo "Deploy complete at $(date)" >> $LOG_FILE