"""Configuration settings for wifi-driver automation."""

import logging
from pathlib import Path

# Project structure
ASSETS_DIR = Path('assets')
DEBUG_DIR = Path('debug_screenshots')

# GUI Interaction settings
MAX_RETRIES = 5
DEFAULT_CONFIDENCE = 0.9
CLICK_INTERVAL = 0.5

# Image recognition settings
USE_GRAYSCALE = True
IMAGE_TIMEOUT = 10  # Max seconds to wait for an image to appear
CONFIDENCE_FALLBACK_LEVELS = [0.9, 0.8, 0.7]  # Try these confidence levels in sequence

# Logging configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_FILE = "driver_automation.log"
