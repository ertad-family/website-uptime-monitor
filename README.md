# Website Uptime Monitor

A Python-based service that monitors website uptime and sends Telegram notifications when status changes occur.

## Features

- Monitors multiple websites for availability
- Sends Telegram notifications on status changes (UP/DOWN)
- Configurable via JSON file
- Logs all checks and status changes
- Runs automatically via cron job

## Setup

1. **Install dependencies:**
   ```bash
   pip3 install requests
   ```

2. **Configure the service:**
   Edit `config.json` to set your Telegram bot credentials and websites to monitor.

3. **Test the monitor:**
   ```bash
   python3 website_monitor_config.py
   ```

4. **Install cron job:**
   ```bash
   ./setup_cron.sh
   ```

## Configuration

Edit `config.json` to customize:
- Telegram bot token and chat ID
- List of websites to monitor
- Timeout settings
- Check interval (used by cron)

## Files

- `website_monitor_config.py` - Main monitoring script with config file support
- `website_monitor.py` - Standalone version with hardcoded values
- `config.json` - Configuration file
- `website_status.json` - Stores website status between runs
- `website_monitor.log` - Log file
- `setup_cron.sh` - Automated cron setup script

## Manual Cron Setup

If you prefer to set up cron manually:
```bash
crontab -e
```

Add this line to run every hour:
```
0 * * * * cd /data/data/com.termux/files/home/website-checker && /usr/bin/python3 website_monitor_config.py >> website_monitor.log 2>&1
```

## Monitoring

View logs:
```bash
tail -f website_monitor.log
```

Check current website status:
```bash
cat website_status.json
```

## Removing the Service

To stop monitoring:
```bash
crontab -l | grep -v 'website_monitor_config.py' | crontab -
```