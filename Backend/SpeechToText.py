import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import mtranslate as mt
import logging
import config

# Setup logger
logger = logging.getLogger("VasanthAssistant.SpeechToText")

# ----------------------------
# CONFIGURATION
# ----------------------------
InputLanguage = config.INPUT_LANGUAGE

# Defining the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace language setting in HTML
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Ensure Data directory exists
config.DATA_DIR.mkdir(parents=True, exist_ok=True)

# Write modified HTML code to file
voice_html_path = config.DATA_DIR / 'Voice.html'
with voice_html_path.open("w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Path to Voice.html
Link = str(voice_html_path.absolute())

# Set Chrome options (prepared but not initialized yet)
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
chrome_options.add_argument(f"--user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

# Global driver variable (initialized lazily)
driver = None

# Define temporary files path
tempDirPath = config.TEMP_DIR
tempDirPath.mkdir(parents=True, exist_ok=True)

# Save assistant status
def SetSubAssistantStatus(Status):
    status_file = tempDirPath / "Status.data"
    with status_file.open("w", encoding="utf-8") as file:
        file.write(Status)

# Format query text
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = [
        "how", "what", "who", "where", "when", "why", "which",
        "whose", "whom", "can you", "what's", "where's", "how's"
    ]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

# Universal translator
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

def _download_chromedriver():
    """Download the correct ChromeDriver manually"""
    import requests
    import zipfile
    import io
    import platform
    
    # Determine correct architecture
    is_64bit = platform.machine().endswith('64')
    arch = 'win64' if is_64bit else 'win32'
    
    # Try multiple versions (prioritize 143 to match current Chrome)
    versions = [
        '143.0.7499.170',  # Match current Chrome version
        '143.0.7499.169',
        '143.0.7499.0',
        '131.0.6778.204',  # Fallback
        '130.0.6723.116',
    ]
    
    # Try to download
    driver_path = config.DATA_DIR / "chromedriver"
    driver_path.mkdir(parents=True, exist_ok=True)
    driver_exe = driver_path / "chromedriver.exe"
    
    # If already exists and works, use it
    if driver_exe.exists():
        logger.info(f"ChromeDriver already exists at {driver_exe}")
        return str(driver_exe)
    
    # Download ChromeDriver
    logger.info(f"Downloading ChromeDriver for {arch}...")
    
    for version in versions:
        url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/{arch}/chromedriver-{arch}.zip"
        logger.info(f"Trying version {version}...")
        
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                logger.info(f"Successfully downloaded ChromeDriver {version}")
                # Extract zip
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                    # Find chromedriver.exe in the zip
                    for file_info in zip_ref.filelist:
                        if file_info.filename.endswith('chromedriver.exe'):
                            # Extract just the exe
                            with zip_ref.open(file_info) as source:
                                with driver_exe.open('wb') as target:
                                    target.write(source.read())
                            logger.info(f"ChromeDriver extracted to {driver_exe}")
                            return str(driver_exe)
                break
        except Exception as e:
            logger.warning(f"Failed to download version {version}: {e}")
            continue
    
    raise RuntimeError("Failed to download ChromeDriver from all sources")

def _initialize_driver():
    """Initialize Chrome WebDriver lazily (only when needed)"""
    global driver
    if driver is not None:
        return driver
    
    try:
        logger.info("Initializing Chrome WebDriver...")
        
        # Download ChromeDriver manually to ensure correct architecture
        chromedriver_path = _download_chromedriver()
        
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Chrome WebDriver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {e}")
        logger.error("Speech recognition will not be available")
        raise RuntimeError(
            f"Chrome WebDriver initialization failed: {e}\n"
            "Please ensure:\n"
            "1. Google Chrome is installed\n"
            "2. You have internet connection (to download ChromeDriver)\n"
            "3. Your antivirus is not blocking the download\n"
            "Speech recognition features will not work without Chrome."
        )

# Perform speech recognition
def SpeechRecognition():
    """Perform speech recognition using Chrome WebDriver"""
    global driver
    
    # Initialize driver on first use
    if driver is None:
        try:
            driver = _initialize_driver()
        except RuntimeError as e:
            logger.error(f"Cannot perform speech recognition: {e}")
            # Return None instead of error message to prevent it from being processed as a command
            return None
    
    try:
        driver.get("file:///" + Link)
        driver.find_element(by=By.ID, value="start").click()

        while True:
            try:
                Text = driver.find_element(by=By.ID, value="output").text
                if Text:
                    driver.find_element(by=By.ID, value="end").click()
                    if "en" in InputLanguage.lower():
                        return QueryModifier(Text)
                    else:
                        SetSubAssistantStatus("Translating ...")
                        return QueryModifier(UniversalTranslator(Text))
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Error during speech recognition: {e}")
        return None  # Return None instead of error message

# Main loop
if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)
    