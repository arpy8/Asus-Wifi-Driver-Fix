"""
WiFi Driver Management Script - Main Module
A script to automate WiFi driver reinstallation on Windows.
"""

import pyuac
import logging
import subprocess
import pyautogui as pg
from utils import (
    setup_logging, take_debug_screenshot, check_screen_resolution,
    safe_key_press, locate_and_click_image
)

logger = logging.getLogger(__name__)

def open_device_manager() -> bool:
    """Open Device Manager through Windows menu with multiple fallback methods.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("Opening Device Manager...")
    try:    
        subprocess.call("control /name Microsoft.DeviceManager")
        subprocess.call("control hdwwiz.cpl")
        return True
    except Exception as e:
        logger.error(f"Failed to open Device Manager: {e}")
        take_debug_screenshot("device_manager_failure")
        return False
    
def reinstall_wifi_driver() -> bool:
    """Main workflow to uninstall and reinstall WiFi driver.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Starting WiFi driver reinstallation process...")
        
        if not locate_and_click_image("network_adapters.png", confidence=0.8, clicks=2):
            logger.error("Could not locate Network Adapters")
            return False
            
        if not locate_and_click_image("wifi_driver.png", confidence=0.8):
            logger.error("Could not locate WiFi driver")
            return False
            
        safe_key_press("delete")
        
        if not locate_and_click_image("uninstall_button.png", confidence=0.8):
            logger.error("Could not find uninstall confirmation button")
            return False
        
        if locate_and_click_image("uninstall_device_box.png", confidence=0.8):
            logger.info("Confirmed uninstall device box option")
        else:
            logger.info("No uninstall device box found, proceeding")
            
        if not locate_and_click_image("action_button.png", confidence=0.8):
            logger.error("Could not find Action menu")
            return False
            
        if not locate_and_click_image("scan_for_hardware_changes.png", confidence=0.8):
            logger.error("Could not find scan for hardware changes option")
            
            if not locate_and_click_image("action_button.png", confidence=0.8, clicks=2):
                logger.error("Could not find Action menu")
                return False
            
            return False
            
        logger.info("WiFi driver successfully reinstalled")
        return True
        
    except Exception as e:
        logger.error(f"Error during WiFi driver reinstallation: {e}")
        take_debug_screenshot("reinstall_error")
        return False

def main() -> None:
    """Main function that orchestrates the driver reinstallation process."""
    try:
        pg.FAILSAFE = True
        
        setup_logging()
        
        check_screen_resolution()
        take_debug_screenshot("initial_state")
        
        if not open_device_manager():
            logger.error("Failed to open Device Manager. Aborting.")
            return
            
        take_debug_screenshot("device_manager_opened")
        
        if reinstall_wifi_driver():
            logger.info("Process completed successfully!")
        else:
            logger.error("Failed to complete WiFi driver reinstallation")
            
    except Exception as e:
        logger.critical(f"Fatal error in main execution: {e}")
        take_debug_screenshot("fatal_error")

if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        print("Re-launching as administrator...")
        pyuac.runAsAdmin()
    else:
        main()