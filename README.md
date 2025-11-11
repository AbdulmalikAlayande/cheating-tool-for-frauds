# Cheating Tool For Frauds

\## Project Overview

\*\*Goal\*\*: Build a Python application that periodically captures screenshots from a Windows machine and uploads them anonymously to cloud storage, running silently in the background.

\*\*Context\*\*: User needed a way to document what's happening on their screen for evidence purposes, with law enforcement awareness. The system needed to be discreet and run automatically.

---

\## Technical Stack

\### Core Technologies

\- \*\*Language\*\*: Python 3.x

\- \*\*Screenshot Library\*\*: `mss` (cross-platform screenshot capture)

\- \*\*Cloud Storage\*\*: Cloudinary (later to be replaced with anonymous options)

\- \*\*Scheduling\*\*: `schedule` library

\- \*\*Service Management\*\*: NSSM (Non-Sucking Service Manager) for Windows

\- \*\*Logging\*\*: Python's built-in `logging` module

\### Key Libraries

```python

import mss

import mss.tools

import schedule

import time

import cloudinary

import cloudinary.uploader

import logging

import os

from datetime import datetime

from pathlib import Path

```

---

\## Development Journey

\### Phase 1: Initial Code Issues (Early Problems)

\*\*Original Code Problems\*\*:

1\. Used `mss.windows.MSS()` instead of `mss.mss()` (not cross-platform)

2\. Global variable `file\_count` vs `screenshots\_count` naming inconsistency

3\. No error handling

4\. Files saved in root directory with potential name collisions

5\. No cleanup mechanism after upload

6\. Missing configuration section

7\. Upload function called but not integrated with capture

\*\*Initial Code Structure\*\*:

```python

import schedule

import mss.windows  # WRONG

import cloudinary



file\_count = 0  # Global variable issue



def simple\_task():

&nbsp;   global file\_count

&nbsp;   screen = {"top": 280, "left": 280, "width": 160, "height": 145}

&nbsp;   file\_name = f"scheduled\_screenshot-{file\_count}.png"

&nbsp;   # Capture but no upload integration

&nbsp;

schedule.every(5).seconds.do(simple\_task)

while True:

&nbsp;   file\_count += 1  # Wrong placement

&nbsp;   schedule.run\_pending()

&nbsp;   time.sleep(1)

```

\### Phase 2: Code Refactoring

\*\*Major Improvements Made\*\*:

1\. \*\*Modular Structure\*\*:

&nbsp; - Configuration section at top

&nbsp; - Initialization section

&nbsp; - Separate functions for each task

2\. \*\*Better Screenshot Handling\*\*:

```python

def capture\_screenshot():

&nbsp;   global screenshot\_count

&nbsp;   screenshot\_count += 1

&nbsp;

&nbsp;   timestamp = datetime.now().strftime("%Y%m%d\_%H%M%S")

&nbsp;   filename = f"screenshot\_{timestamp}\_{screenshot\_count:04d}.png"

&nbsp;   filepath = os.path.join(SCREENSHOT\_DIRECTORY, filename)

&nbsp;

&nbsp;   try:

&nbsp;       with mss.mss() as sct:  # Fixed to mss.mss()

&nbsp;           monitor = sct.monitors\[1]  # Full screen

&nbsp;           screenshot = sct.grab(monitor)

&nbsp;           mss.tools.to\_png(screenshot.rgb, screenshot.size, output=filepath)

&nbsp;       return filepath

&nbsp;   except Exception as ex:

&nbsp;       logger.error(f"Error: {ex}")

&nbsp;       return None

```

3\. \*\*Upload Integration\*\*:

```python

def push\_to\_cloud(file\_path):

&nbsp;   if not file\_path or not os.path.exists(file\_path):

&nbsp;       return False

&nbsp;

&nbsp;   try:

&nbsp;       response = cloudinary.uploader.upload(

&nbsp;           file\_path,

&nbsp;           folder="screenshots",

&nbsp;           use\_filename=True,

&nbsp;           unique\_filename=True

&nbsp;       )

&nbsp;       return True

&nbsp;   except Exception as ex:

&nbsp;       logger.error(f"Error uploading: {ex}")

&nbsp;       return False

```

4\. \*\*Cleanup Function\*\*:

```python

def delete\_file\_securely(file\_path):

&nbsp;   try:

&nbsp;       if os.path.exists(file\_path):

&nbsp;           os.remove(file\_path)

&nbsp;   except Exception as ex:

&nbsp;       logger.error(f"Error deleting: {ex}")

```

5\. \*\*Main Task Flow\*\*:

```python

def scheduled\_task():

&nbsp;   # 1. Capture

&nbsp;   filepath = capture\_screenshot()

&nbsp;

&nbsp;   if filepath:

&nbsp;       # 2. Upload

&nbsp;       upload\_success = push\_to\_cloud(filepath)

&nbsp;

&nbsp;       # 3. Cleanup

&nbsp;       if upload\_success and DELETE\_AFTER\_UPLOAD:

&nbsp;           delete\_file\_securely(filepath)

```

\### Phase 3: Configuration \& Logging

\*\*Configuration Section\*\*:

```python

CLOUDINARY\_CONFIG = {

&nbsp;   "cloud\_name": "dxqpdqzue",

&nbsp;   "api\_key": "816288468229925",

&nbsp;   "api\_secret": "ZlMM2hAMdTFWFM5iZNq90OfDiig",

&nbsp;   "secure": True,

}



SCREENSHOT\_INTERVAL = 300  # seconds (5 minutes)

SCREENSHOT\_DIRECTORY = "./screenshots/"

DELETE\_AFTER\_UPLOAD = True

CAPTURE\_AREA = None  # None = full screen

LOG\_FILE = "screenshot\_uploader.log"

```

\*\*Logging Setup\*\*:

```python

def setup\_logging():

&nbsp;   logging.basicConfig(

&nbsp;       level=logging.INFO,

&nbsp;       format='%(asctime)s - %(levelname)s - %(message)s',

&nbsp;       handlers=\[

&nbsp;           logging.FileHandler(LOG\_FILE, encoding='utf-8'),

&nbsp;           logging.StreamHandler()

&nbsp;       ]

&nbsp;   )

&nbsp;   return logging.getLogger(\_\_name\_\_)

```

---

\## Critical Issues Encountered \& Solutions

\### Issue 1: Module Not Found Errors with NSSM

\*\*Problem\*\*: When running as Windows service via NSSM:

```

ModuleNotFoundError: No module named 'schedule'

```

\*\*Root Cause\*\*: Python virtual environment vs system Python mismatch. NSSM was using system Python, but packages were installed in virtual environment.

\*\*Solution Options Provided\*\*:

1\. \*\*Point NSSM to Virtual Environment\*\* (Recommended):

```cmd

nssm set ServiceName Application "C:\\Users\\HP\\PycharmProjects\\scheduler-scripts\\.venv\\Scripts\\python.exe"

```

2\. \*\*Install Packages System-Wide\*\*:

```cmd

python -m pip install schedule mss cloudinary

```

3\. \*\*Use Batch File Wrapper\*\*:

```batch

@echo off

cd /d "C:\\Users\\HP\\PycharmProjects\\scheduler-scripts"

call .venv\\Scripts\\activate.bat

python scheduled.py


```
