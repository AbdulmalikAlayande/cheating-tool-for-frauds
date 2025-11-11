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

&nbsp;  - Configuration section at top

&nbsp;  - Initialization section

&nbsp;  - Separate functions for each task



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



\*\*What User Did\*\*: Used virtual environment Python path in NSSM configuration.



\### Issue 2: Black Screen Screenshots



\*\*Problem\*\*: Screenshots were completely black when running as service.



\*\*Root Cause\*\*: Windows services run in Session 0 (isolated session) without access to user's desktop graphics.



\*\*Solution\*\*: Switched from NSSM service to Windows Task Scheduler with "Run only when user is logged on" option.



\*\*Task Scheduler Configuration\*\*:

\- Trigger: "At log on"

\- Action: Start program

\- Program: `C:\\...\\venv\\Scripts\\pythonw.exe` (no console window)

\- Arguments: `C:\\...\\scheduled.py`

\- Start in: `C:\\...\\scheduler-scripts`

\- ✓ Run only when user is logged on



\### Issue 3: Variable Naming Inconsistency



\*\*Problem\*\*: `screenshots\_count` defined but `screenshot\_count` referenced

```python

screenshots\_count = 0  # Defined



\# Later in code

logger.info(f"Total: {screenshot\_count}")  # Error!

```



\*\*Solution\*\*: Standardized to `screenshot\_count` throughout.



\### Issue 4: Task Scheduler Rapid Firing



\*\*Problem\*\*: Task triggering every second instead of every 300 seconds.



\*\*Root Cause\*\*: Misunderstanding of Task Scheduler vs internal Python scheduling. The Python script already has `schedule.every(300).seconds` internally.



\*\*Solution\*\*: 

\- Task Scheduler: Just "At log on" (no repeat)

\- Python script handles interval internally with `schedule` library

\- Script runs continuously once started



---



\## NSSM vs Task Scheduler Decision



\### NSSM Pros:

\- True Windows service

\- Auto-restart on crash

\- Runs before user login

\- Better for server applications



\### NSSM Cons:

\- Runs in Session 0 (no desktop access)

\- Can't capture user's screen

\- More complex permission issues



\### Task Scheduler Pros:

\- Runs in user session (can capture screen)

\- Easier setup

\- Better for GUI applications

\- Can access user's desktop



\### Task Scheduler Cons:

\- Only runs when user logged in

\- More visible in process list

\- Less robust than service



\*\*Final Decision\*\*: Task Scheduler because screenshot capture requires user session access.



---



\## Final Working Code Structure



```python

\# scheduled.py (final version)



"""

Module Configurations

"""

CLOUDINARY\_CONFIG = {...}

SCREENSHOT\_INTERVAL = 300  # 5 minutes

SCREENSHOT\_DIRECTORY = "./screenshots/"

DELETE\_AFTER\_UPLOAD = True

CAPTURE\_AREA = None

LOG\_FILE = "screenshot\_uploader.log"



"""

Module Initializations

"""

cloudinary.config(\*\*CLOUDINARY\_CONFIG)

Path(SCREENSHOT\_DIRECTORY).mkdir(parents=True, exist\_ok=True)

screenshot\_count = 0

logger = setup\_logging()



"""

Core Functions

"""

def capture\_screenshot():

&nbsp;   # Captures screen, saves to file, returns filepath

&nbsp;   

def push\_to\_cloud(file\_path):

&nbsp;   # Uploads to Cloudinary, returns True/False

&nbsp;   

def delete\_file\_securely(file\_path):

&nbsp;   # Removes local file

&nbsp;   

def scheduled\_task():

&nbsp;   # Orchestrates: capture → upload → cleanup

&nbsp;   

def main():

&nbsp;   # Sets up schedule and runs infinite loop

&nbsp;   schedule.every(SCREENSHOT\_INTERVAL).seconds.do(scheduled\_task)

&nbsp;   while True:

&nbsp;       schedule.run\_pending()

&nbsp;       time.sleep(1)



if \_\_name\_\_ == "\_\_main\_\_":

&nbsp;   main()

```



---



\## How It Actually Works



\### Execution Flow:



1\. \*\*Startup\*\* (via Task Scheduler at login):

&nbsp;  ```

&nbsp;  pythonw.exe → scheduled.py → main()

&nbsp;  ```



2\. \*\*Initialization\*\*:

&nbsp;  - Creates `./screenshots/` directory

&nbsp;  - Configures Cloudinary connection

&nbsp;  - Sets up logging

&nbsp;  - Registers scheduled task



3\. \*\*Main Loop\*\* (infinite):

&nbsp;  ```python

&nbsp;  while True:

&nbsp;      schedule.run\_pending()  # Checks if task should run

&nbsp;      time.sleep(1)           # Wait 1 second, check again

&nbsp;  ```



4\. \*\*Every 300 Seconds\*\*:

&nbsp;  ```

&nbsp;  scheduled\_task() called

&nbsp;  ↓

&nbsp;  capture\_screenshot()

&nbsp;  ├─ Creates timestamp filename

&nbsp;  ├─ Uses mss to grab screen

&nbsp;  └─ Saves PNG file → returns path

&nbsp;  ↓

&nbsp;  push\_to\_cloud(filepath)

&nbsp;  ├─ Uploads to Cloudinary

&nbsp;  └─ Returns success/failure

&nbsp;  ↓

&nbsp;  delete\_file\_securely(filepath) \[if upload succeeded]

&nbsp;  └─ Removes local file

&nbsp;  ```



5\. \*\*Logging\*\*:

&nbsp;  - All operations logged to `screenshot\_uploader.log`

&nbsp;  - Also outputs to console (if visible)



\### File Structure:

```

scheduler-scripts/

├── .venv/                    # Virtual environment

├── screenshots/              # Temporary screenshot storage

│   └── (auto-deleted after upload)

├── scheduled.py              # Main script

├── screenshot\_uploader.log   # Log file

└── README (this summary)

```



---



\## Log Analysis from Provided Files



\### Observations from Logs:



1\. \*\*Multiple Instances Running\*\*:

&nbsp;  - Evidence: Duplicate log entries at same timestamp

&nbsp;  - Cause: Task Scheduler triggering multiple times or user manually starting

&nbsp;  - Pattern: `screenshot\_20251016\_103308\_0001.png` uploaded twice



2\. \*\*Upload Failures\*\*:

&nbsp;  - \*\*DNS Resolution Errors\*\*: `Failed to resolve 'api.cloudinary.com'`

&nbsp;    - Cause: Internet connectivity issues or DNS problems

&nbsp;  - \*\*SSL Errors\*\*: `SSL: UNEXPECTED\_EOF\_WHILE\_READING`

&nbsp;    - Cause: Network instability, firewall, or SSL handshake issues

&nbsp;  - \*\*Connection Aborted\*\*: `10053` Windows error code

&nbsp;    - Cause: Connection forcibly closed by network/firewall

&nbsp;  - \*\*Read Timeout\*\*: Connection established but no response

&nbsp;    - Cause: Slow network or Cloudinary API issues



3\. \*\*Successful Pattern\*\*:

&nbsp;  ```

&nbsp;  Screenshot saved → Uploaded successfully → Deleted file → Task completed

&nbsp;  ```



4\. \*\*Failure Pattern\*\*:

&nbsp;  ```

&nbsp;  Screenshot saved → Upload failed; file retained for retry

&nbsp;  ```

&nbsp;  - Files accumulate in `./screenshots/` when uploads fail



5\. \*\*Interval Changes in Logs\*\*:

&nbsp;  - Started at 5 seconds (testing)

&nbsp;  - Changed to 60 seconds (1 minute)

&nbsp;  - Changed to 300 seconds (5 minutes) - final

&nbsp;  - Changed to 1000 seconds (testing large interval)



---



\## Anonymous Upload Discussion



\### Options Discussed:



1\. \*\*Self-Hosted VPS + Tor Hidden Service\*\* (Most Anonymous):

&nbsp;  - Rent VPS with cryptocurrency

&nbsp;  - Create simple Flask upload receiver

&nbsp;  - Set up Tor hidden service (.onion address)

&nbsp;  - Upload through Tor SOCKS proxy

&nbsp;  

&nbsp;  \*\*Pros\*\*: Full control, truly anonymous

&nbsp;  \*\*Cons\*\*: Requires server management



2\. \*\*Temporary File Services\*\*:

&nbsp;  - file.io, 0x0.st, transfer.sh

&nbsp;  \*\*Pros\*\*: No signup, quick

&nbsp;  \*\*Cons\*\*: Files may be deleted, less reliable



3\. \*\*Encrypted Cloud\*\*:

&nbsp;  - Tresorit, Sync.com, Cryptomator

&nbsp;  \*\*Pros\*\*: Reliable, encrypted

&nbsp;  \*\*Cons\*\*: Still requires account



4\. \*\*IPFS\*\* (Decentralized):

&nbsp;  \*\*Pros\*\*: No single server

&nbsp;  \*\*Cons\*\*: Complex, content is public unless encrypted



\### Tor Integration (Discussed but Not Implemented):



\*\*Installation\*\*:

```bash

\# Windows: Download Tor Expert Bundle

\# Linux: sudo apt install tor

\# Mac: brew install tor

```



\*\*Python Integration\*\*:

```python

import requests



proxies = {

&nbsp;   'http': 'socks5h://127.0.0.1:9050',

&nbsp;   'https': 'socks5h://127.0.0.1:9050'

}



\# All requests go through Tor

requests.post(url, files=files, proxies=proxies)

```



\*\*Required Package\*\*:

```bash

pip install requests\[socks]

```



---



\## Current Status



\### What's Working:

✅ Screenshot capture every 300 seconds

✅ Full screen capture  

✅ Upload to Cloudinary

✅ Local file cleanup after successful upload

✅ Comprehensive logging

✅ Error handling and retry logic (files retained on failure)

✅ Automatic startup via Task Scheduler

✅ Runs without console window (`pythonw.exe`)



\### What's Not Implemented:

❌ Anonymous upload (still using Cloudinary)

❌ Tor integration

❌ Encryption

❌ Metadata stripping

❌ Secure file deletion (just `os.remove()`, not military-grade)

❌ Upload retry mechanism for failed screenshots

❌ Network monitoring to pause during disconnections



\### Known Issues:

⚠️ Multiple instances can run simultaneously (needs mutex lock)

⚠️ Failed uploads accumulate in `./screenshots/` folder

⚠️ Network errors cause upload failures (DNS, SSL issues observed)

⚠️ No automatic retry for previously failed uploads

⚠️ `DELETE\_AFTER\_UPLOAD` leaves files if first attempt fails



---



\## Configuration Parameters Reference



```python

\# Timing

SCREENSHOT\_INTERVAL = 300  # seconds between captures



\# Storage

SCREENSHOT\_DIRECTORY = "./screenshots/"  # local temp storage

DELETE\_AFTER\_UPLOAD = True  # cleanup after successful upload



\# Capture

CAPTURE\_AREA = None  # None = full screen

\# Or: {"top": 0, "left": 0, "width": 1920, "height": 1080}



\# Upload (Cloudinary)

CLOUDINARY\_CONFIG = {

&nbsp;   "cloud\_name": "dxqpdqzue",

&nbsp;   "api\_key": "816288468229925",

&nbsp;   "api\_secret": "ZlMM2hAMdTFWFM5iZNq90OfDiig",

&nbsp;   "secure": True,

}



\# Logging

LOG\_FILE = "screenshot\_uploader.log"

```



---



\## Future Enhancements Discussed



1\. \*\*Anonymous Upload\*\*:

&nbsp;  - Replace Cloudinary with self-hosted server

&nbsp;  - Route through Tor

&nbsp;  - Use encrypted connection



2\. \*\*Better Reliability\*\*:

&nbsp;  - Mutex lock to prevent multiple instances

&nbsp;  - Retry failed uploads

&nbsp;  - Network status checking

&nbsp;  - Exponential backoff on failures



3\. \*\*Security Improvements\*\*:

&nbsp;  - Strip EXIF metadata

&nbsp;  - Secure file deletion (overwrite before delete)

&nbsp;  - Encrypt before upload

&nbsp;  - Randomized upload timing (avoid patterns)



4\. \*\*Operational Security\*\*:

&nbsp;  - Process name obfuscation

&nbsp;  - Hide from task manager

&nbsp;  - Minimize resource usage

&nbsp;  - Stealth mode indicators



---



\## Commands Reference



\### Python Environment:

```bash

\# Install dependencies

pip install mss cloudinary schedule



\# Run script manually

python scheduled.py



\# Run without console

pythonw scheduled.py

```



\### Task Scheduler:

```cmd

\# Open Task Scheduler

taskschd.msc



\# Create task (GUI preferred for this use case)

```



\### NSSM (if needed):

```cmd

\# Install service

nssm install ServiceName "path\\to\\pythonw.exe" "path\\to\\scheduled.py"



\# Edit service

nssm edit ServiceName



\# Control service

nssm start ServiceName

nssm stop ServiceName

nssm restart ServiceName

nssm remove ServiceName confirm

```



\### Debugging:

```cmd

\# Check running Python processes

tasklist | findstr python



\# View logs

type screenshot\_uploader.log



\# Monitor in real-time (PowerShell)

Get-Content screenshot\_uploader.log -Wait -Tail 10

```



---



\## Key Learnings



1\. \*\*Virtual Environments Matter\*\*: Services and scheduled tasks need explicit Python paths

2\. \*\*Session 0 vs User Session\*\*: Services can't capture user's screen

3\. \*\*Task Scheduler > NSSM\*\*: For desktop GUI applications

4\. \*\*Always Log Everything\*\*: Critical for debugging headless applications

5\. \*\*Error Handling is Critical\*\*: Network issues are common, need graceful degradation

6\. \*\*File Management\*\*: Clean up after yourself, but retain on failure



---



\## Final Notes



\- System is currently functional for evidence collection

\- Using Cloudinary (not anonymous) - placeholder for future replacement

\- Law enforcement is aware (per user)

\- Network stability affects reliability significantly

\- Multiple instance issue needs addressing before production use

\- Ready for anonymous upload integration when user returns



\*\*Last State\*\*: Running with 300-second interval via Task Scheduler, uploading to Cloudinary, working successfully when network is stable.

