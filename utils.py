"""Utility functions for the wifi-driver application."""

import time
import config
import logging
import datetime
import subprocess
import pyautogui as pg
from typing import Tuple, Union

logger = logging.getLogger(__name__)

def setup_logging():
    """Configure logging for the application."""
    config.DEBUG_DIR.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )

def take_debug_screenshot(name_prefix: str) -> str:
    """Take a debug screenshot and save it with timestamp.
    
    Args:
        name_prefix: Prefix for the screenshot filename
        
    Returns:
        Path to the saved screenshot
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name_prefix}_{timestamp}.png"
    filepath = config.DEBUG_DIR / filename
    
    try:
        pg.screenshot(str(filepath))
        logger.info(f"Debug screenshot saved: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Failed to take screenshot: {e}")
        return ""

def check_screen_resolution() -> Tuple[int, int]:
    """Check and log screen resolution.
    
    Returns:
        Tuple containing width and height
    """
    width, height = pg.size()
    logger.info(f"Screen resolution: {width}x{height}")
    return width, height

def safe_click(x: int, y: int, interval: float = config.CLICK_INTERVAL, clicks: int = 1) -> bool:
    """Safely click at the specified coordinates with error handling.
    
    Args:
        x: X coordinate
        y: Y coordinate
        interval: Time to wait after click
        clicks: Number of clicks
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Clicking at ({x}, {y})")
        pg.click(x, y, clicks=clicks)
        time.sleep(interval)
        return True
    except Exception as e:
        logger.error(f"Click operation failed at ({x}, {y}): {e}")
        take_debug_screenshot("click_failure")
        return False

def wait_for_image(image_path: str, 
                  timeout: int = config.IMAGE_TIMEOUT, 
                  confidence: float = config.DEFAULT_CONFIDENCE,
                  grayscale: bool = config.USE_GRAYSCALE):
    """Wait for an image to appear on screen with timeout.
    
    Args:
        image_path: Path to the image file relative to assets directory
        timeout: Maximum seconds to wait for the image
        confidence: Confidence level for image detection
        grayscale: Whether to use grayscale matching
        
    Returns:
        Location box if image found, None otherwise
    """
    image_full_path = config.ASSETS_DIR / image_path
    if not image_full_path.exists():
        logger.error(f"Image file not found: {image_full_path}")
        return None
        
    logger.info(f"Waiting for image to appear: {image_path} (timeout: {timeout}s)")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            for conf in [confidence] + [c for c in config.CONFIDENCE_FALLBACK_LEVELS if c < confidence]:
                location = pg.locateOnScreen(str(image_full_path), confidence=conf, grayscale=grayscale)
                if location:
                    logger.info(f"Image {image_path} found at {location} (confidence: {conf})")
                    return location
            
            time.sleep(0.1)
        except Exception as e:
            logger.warning(f"Error while searching for {image_path}: {e}")
            time.sleep(0.5)
            
    logger.warning(f"Image {image_path} not found after {timeout} seconds")
    take_debug_screenshot(f"not_found_{image_path.replace('.png', '')}")
    return None

def locate_and_click_image(image_path: str, 
                          timeout: int = config.IMAGE_TIMEOUT,
                          confidence: float = config.DEFAULT_CONFIDENCE, 
                          grayscale: bool = config.USE_GRAYSCALE,
                          clicks: int = 1) -> bool:
    """Locate an image on screen and click its center with timeout.
    
    Args:
        image_path: Path to the image file relative to assets directory
        timeout: Maximum seconds to wait for the image
        confidence: Confidence level for image detection
        grayscale: Whether to use grayscale matching
        clicks: Number of clicks
        
    Returns:
        True if successful, False otherwise
    """
    location = wait_for_image(image_path, timeout, confidence, grayscale)
    
    if location:
        button_center = pg.center(location)
        return safe_click(button_center.x, button_center.y, clicks=clicks)
    
    return False

def safe_key_press(key: Union[str, list], interval: float = config.CLICK_INTERVAL) -> bool:
    """Safely press a key or key combination with error handling.
    
    Args:
        key: Key or key combination to press
        interval: Time to wait after key press
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if isinstance(key, list):
            logger.info(f"Pressing key combination: {key}")
            pg.hotkey(*key)
        else:
            logger.info(f"Pressing key: {key}")
            pg.press(key)
            
        time.sleep(interval)
        return True
    except Exception as e:
        logger.error(f"Key press operation failed for {key}: {e}")
        take_debug_screenshot("key_press_failure")
        return False

def safe_write(text: str, interval: float = config.CLICK_INTERVAL) -> bool:
    """Safely write text with error handling.
    
    Args:
        text: Text to write
        interval: Time to wait after writing
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Writing text: {text}")
        pg.write(text)
        time.sleep(interval)
        return True
    except Exception as e:
        logger.error(f"Write operation failed for '{text}': {e}")
        take_debug_screenshot("write_failure")
        return False


def open_device_manager() -> bool:
    try:
        subprocess.call("control /name Microsoft.DeviceManager")
        subprocess.call("control hdwwiz.cpl")
        return True
    except Exception as e:
        logger.error(f"Failed to open Device Manager: {e}")
        take_debug_screenshot("device_manager_failure")
        return False

def close_device_manager() -> bool:
    """Safely close the Device Manager window.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Closing Device Manager...")
            
        if locate_and_click_image("device_manager_close.png", confidence=0.95, clicks=2):
            logger.info("Device Manager closed successfully via close button")
            return True
            
        logger.warning("Could not locate Device Manager window to close")
        take_debug_screenshot("device_manager_close_failure")
        return False
    except Exception as e:
        logger.error(f"Failed to close Device Manager: {e}")
        take_debug_screenshot("device_manager_close_error")
        return False


if __name__ == "__main__":
    import pyuac
    
    if not pyuac.isUserAdmin():
        print("Re-launching as administrator...")
        pyuac.runAsAdmin()
    else:
        open_device_manager()