#!/usr/bin/env python3
import json
import os
import time
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
import requests
from requests.exceptions import RequestException, Timeout

TELEGRAM_BOT_TOKEN = "7640097316:AAH4iQL8y4oaHPXsxGjZtNmUto2rBM6WYJ8"
TELEGRAM_CHAT_ID = "303566145"
STATE_FILE = "website_status.json"
LOG_FILE = "website_monitor.log"
TIMEOUT_SECONDS = 30

WEBSITES = [
    "https://mandarini.wedding",
    "https://ori.wedding",
    "https://sami.wedding",
    "https://vow.legal",
    "https://stas.video"
]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_state() -> Dict[str, bool]:
    """Load the previous state of websites from file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading state file: {e}")
    return {}


def save_state(state: Dict[str, bool]) -> None:
    """Save the current state of websites to file."""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving state file: {e}")


def check_website(url: str) -> Tuple[bool, str, Optional[int]]:
    """
    Check if a website is up and return status.
    Returns: (is_up, error_message, status_code)
    """
    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS, allow_redirects=True)
        status_code = response.status_code
        
        if status_code == 200:
            return True, "OK", status_code
        else:
            return False, f"HTTP {status_code}", status_code
            
    except Timeout:
        return False, f"Timeout after {TIMEOUT_SECONDS}s", None
    except RequestException as e:
        error_msg = str(e)
        if "ConnectionError" in error_msg:
            return False, "Connection failed", None
        elif "SSLError" in error_msg:
            return False, "SSL error", None
        else:
            return False, f"Error: {error_msg[:100]}", None
    except Exception as e:
        return False, f"Unexpected error: {str(e)[:100]}", None


def send_telegram_message(message: str) -> bool:
    """Send a message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            logger.info("Telegram message sent successfully")
            return True
        else:
            logger.error(f"Failed to send Telegram message: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        return False


def format_status_message(url: str, is_up: bool, error_msg: str, status_code: Optional[int]) -> str:
    """Format a status change message for Telegram."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if is_up:
        emoji = "✅"
        status = "UP"
        details = f"Status code: {status_code}"
    else:
        emoji = "🔴"
        status = "DOWN"
        details = f"Error: {error_msg}"
    
    message = f"{emoji} <b>{url}</b>\n"
    message += f"Status: <b>{status}</b>\n"
    message += f"{details}\n"
    message += f"Time: {timestamp}"
    
    return message


def main():
    """Main monitoring function."""
    logger.info("Starting website monitoring check")
    
    previous_state = load_state()
    current_state = {}
    status_changed = []
    
    for website in WEBSITES:
        logger.info(f"Checking {website}")
        is_up, error_msg, status_code = check_website(website)
        current_state[website] = is_up
        
        was_up = previous_state.get(website, True)
        
        if is_up != was_up:
            status_changed.append((website, is_up, error_msg, status_code))
            logger.warning(f"Status change detected for {website}: {'UP' if is_up else 'DOWN'}")
        
        logger.info(f"{website}: {'UP' if is_up else 'DOWN'} - {error_msg}")
    
    if status_changed:
        for website, is_up, error_msg, status_code in status_changed:
            message = format_status_message(website, is_up, error_msg, status_code)
            send_telegram_message(message)
            time.sleep(1)
    
    save_state(current_state)
    logger.info(f"Check completed. {len(status_changed)} status changes detected.")


if __name__ == "__main__":
    main()