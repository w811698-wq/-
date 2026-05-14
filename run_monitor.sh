#!/bin/bash

SCRIPT_DIR="/workspace"
PYTHON_BIN="/usr/bin/python3"
LOG_FILE="$SCRIPT_DIR/amazon_monitor.log"

echo "==================================================" >> $LOG_FILE
echo "Amazon Monitor 执行时间: $(date)" >> $LOG_FILE

cd $SCRIPT_DIR
$PYTHON_BIN $SCRIPT_DIR/amazon_monitor.py >> $LOG_FILE 2>&1

echo "执行完成: $(date)" >> $LOG_FILE
echo "==================================================" >> $LOG_FILE
