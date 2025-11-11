import logging
import os.path
from datetime import datetime
from pathlib import Path

import schedule
import mss
import mss.tools
import time
import cloudinary
import cloudinary.uploader

"""
Module Configurations
"""
CLOUDINARY_CONFIG = {
    "cloud_name": "dxqpdqzue",
    "api_key": "816288468229925",
    "api_secret": "ZlMM2hAMdTFWFM5iZNq90OfDiig",
    "secure": True,
}

SCREENSHOT_INTERVAL = 300
SCREENSHOT_DIRECTORY = "./screenshots/"
DELETE_AFTER_UPLOAD = True
CAPTURE_AREA = None
LOG_FILE = "screenshot_uploader.log"

def setup_logging():
    log_dir = os.path.dirname(LOG_FILE) or "."
    if log_dir != ".":
        Path(log_dir).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

"""
Module Initializations
"""
cloudinary.config(**CLOUDINARY_CONFIG)
Path(SCREENSHOT_DIRECTORY).mkdir(parents=True, exist_ok=True)
screenshots_count = 0

"""
Module Functions
"""


def capture_screenshot():
    global screenshots_count
    screenshots_count += 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}_{screenshots_count:04d}.png"
    filepath = os.path.join(SCREENSHOT_DIRECTORY, filename)

    try:
        with mss.mss() as sct:
            if CAPTURE_AREA is None:
                monitor = sct.monitors[1]
            else:
                monitor = CAPTURE_AREA

            screenshot = sct.grab(monitor)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
        logger.info(f"Screenshot saved: {filepath}")
        return filepath
    except Exception as ex:
        logger.error(f"Error capturing screenshot: {ex}")
        return None


def push_to_cloud(file_path):
    if not file_path or not os.path.exists(file_path):
        logger.error("File does not exist for upload. Aborting upload.")
        return False

    try:
        response = cloudinary.uploader.upload(
            file_path,
            folder="screenshots",
            use_filename=True,
            unique_filename=True
        )
        logger.info(f"Uploaded successfully: {response.get('secure_url', 'N/A')}")
        return True
    except Exception as ex:
        logger.error(f"Error uploading to Cloudinary: {ex}")
        return False


def delete_file_securely(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
        else:
            logger.warning(f"File not found for deletion: {file_path}")
    except Exception as ex:
        logger.error(f"Error deleting file: {ex}")


def scheduled_task():
    file_path = capture_screenshot()
    if file_path:
        upload_successful = push_to_cloud(file_path)
        if upload_successful and DELETE_AFTER_UPLOAD:
            delete_file_securely(file_path)
        elif not upload_successful:
            logger.warning("Upload failed; file retained for retry.")
    logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Task completed.")


def main():
    logger.info("=" * 70)
    logger.info("Screenshot Capture & Upload System - STARTED")
    logger.info("=" * 70)
    logger.info(f"Interval: Every {SCREENSHOT_INTERVAL} seconds")
    logger.info(f"Capture area: {'Full screen' if CAPTURE_AREA is None else 'Custom area'}")
    logger.info(f"Upload destination: Cloudinary ({CLOUDINARY_CONFIG['cloud_name']})")
    logger.info(f"Delete after upload: {DELETE_AFTER_UPLOAD}")
    logger.info(f"Log file: screenshot_uploader.log")
    logger.info("=" * 70)
    logger.info("Press Ctrl+C to stop (or stop the NSSM service)\n")

    schedule.every(SCREENSHOT_INTERVAL).seconds.do(scheduled_task)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 70)
        logger.info("SHUTDOWN INITIATED")
        logger.info("=" * 70)
        logger.info(f"Total screenshots captured: {screenshots_count}")
        logger.info("Screenshot capture system stopped.")
        logger.info("=" * 70)
    except Exception as ex:
        logger.critical(f"FATAL ERROR: {ex}")
        raise


if __name__ == "__main__":
    main()

