#!/usr/bin/env python3
"""
Huntarr [Sonarr Edition] - Python Version
Main entry point for the application
"""

import time
import sys
import os
from utils.logger import logger
from config import HUNT_MODE, SLEEP_DURATION, MINIMUM_DOWNLOAD_QUEUE_SIZE, log_configuration
from missing import process_missing_episodes
from upgrade import process_cutoff_upgrades
from state import check_state_reset, calculate_reset_time
from api import get_download_queue_size

def main_loop() -> None:
    """Main processing loop for Huntarr-Sonarr"""
    
    # Log welcome message for web interface
    logger.info("=== Huntarr [Sonarr Edition] Starting ===")
    logger.info("Web interface available at http://YOUR_SERVER_IP:8988")
    logger.info("GitHub: https://github.com/plexguide/huntarr-sonarr")
    
    while True:
        # Check if state files need to be reset
        check_state_reset()
        
        logger.info(f"=== Starting Huntarr-Sonarr cycle ===")
        
        # Track if any processing was done in this cycle
        processing_done = False

        # Check if we should ignore the download queue size or if we are below the minimum queue size
        download_queue_size = get_download_queue_size()
        if MINIMUM_DOWNLOAD_QUEUE_SIZE < 0 or (MINIMUM_DOWNLOAD_QUEUE_SIZE >= 0 and download_queue_size <= MINIMUM_DOWNLOAD_QUEUE_SIZE):
        
            # Process shows/episodes based on HUNT_MODE
            if HUNT_MODE in ["missing", "both"]:
                if process_missing_episodes():
                    processing_done = True
                    
            if HUNT_MODE in ["upgrade", "both"]:
                if process_cutoff_upgrades():
                    processing_done = True

        else:
            logger.info(f"Download queue size ({download_queue_size}) is above the minimum threshold ({MINIMUM_DOWNLOAD_QUEUE_SIZE}). Skipped processing.")

        # Calculate time until the next reset
        calculate_reset_time()
        
        # Sleep at the end of the cycle only
        logger.info(f"Cycle complete. Sleeping {SLEEP_DURATION}s before next cycle...")
        logger.info("⭐ Tool Great? Donate @ https://donate.plex.one for Daughter's College Fund!")
        logger.info("Web interface available at http://YOUR_SERVER_IP:8988")
        
        # Sleep with progress updates for the web interface
        sleep_start = time.time()
        sleep_end = sleep_start + SLEEP_DURATION
        
        while time.time() < sleep_end:
            # Sleep in smaller chunks for more responsive shutdown
            time.sleep(min(10, sleep_end - time.time()))
            
            # Every minute, log the remaining sleep time for web interface visibility
            if int((time.time() - sleep_start) % 60) == 0 and time.time() < sleep_end - 10:
                remaining = int(sleep_end - time.time())
                logger.debug(f"Sleeping... {remaining}s remaining until next cycle")

if __name__ == "__main__":
    # Log configuration settings
    log_configuration(logger)

    try:
        main_loop()
    except KeyboardInterrupt:
        logger.info("Huntarr-Sonarr stopped by user.")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)