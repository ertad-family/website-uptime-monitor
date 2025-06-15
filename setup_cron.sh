#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="$SCRIPT_DIR/website_monitor_config.py"
LOG_FILE="$SCRIPT_DIR/website_monitor.log"

echo "Website Monitor Cron Setup"
echo "========================="

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

echo "Installing required Python packages..."
pip3 install requests

echo ""
echo "Making script executable..."
chmod +x "$PYTHON_SCRIPT"

CRON_ENTRY="0 * * * * cd $SCRIPT_DIR && /usr/bin/python3 $PYTHON_SCRIPT >> $LOG_FILE 2>&1"

echo ""
echo "Current crontab:"
crontab -l 2>/dev/null || echo "No existing crontab"

echo ""
echo "Adding cron job to run every hour..."

(crontab -l 2>/dev/null | grep -v "$PYTHON_SCRIPT" ; echo "$CRON_ENTRY") | crontab -

echo ""
echo "Updated crontab:"
crontab -l

echo ""
echo "Setup complete! The monitor will run every hour."
echo ""
echo "To test the script now, run:"
echo "  cd $SCRIPT_DIR && python3 website_monitor_config.py"
echo ""
echo "To view logs:"
echo "  tail -f $LOG_FILE"
echo ""
echo "To remove the cron job:"
echo "  crontab -l | grep -v '$PYTHON_SCRIPT' | crontab -"