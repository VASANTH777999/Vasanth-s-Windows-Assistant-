# ==============================
# IMPORTS
# ==============================
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from AppOpener import open as appopen, close as appclose  # Open/close apps
from webbrowser import open as webopen                    # Open URLs in browser
from pywhatkit import search, playonyt                    # Google & YouTube
from bs4 import BeautifulSoup                             # Parse HTML
from rich import print                                    # Styled console output
from groq import Groq                                     # Groq AI client
import subprocess                                         # System-level commands
import requests                                           # HTTP requests
import keyboard                                           # Keyboard actions
import asyncio                                            # Async tasks
import os                                                 # OS utilities
import logging

# Import centralized configuration
import config

# Setup logger
logger = logging.getLogger("VasanthAssistant.Automation")

# ==============================
# CONFIG
# ==============================
Username = config.USERNAME

classes = [
    "zCubwf", "hgKEIc", "LiK0U syirc", "Z6Lcw",
    "gsrt vk_bk FzvWSb YwPhnf", "pcq6ce",
    "tw-data-text tw-text-small tw-ta", "I7zdrc",
    "O5uR6d LiK0U", "vL7y6d",
    "webanswers-webanswers-table__webanswers-table",
    "dDoNo ikb4Bb gsrt", "sXLa0e", "LiK0YKe",
    "vP4rgg", "q3vWpe", "kno-rdesc", "SPZz6b"
]

useragent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/100.0.4896.75 Safari/537.36"
)

# Initialize Groq client with API key from config
try:
    client = Groq(api_key=config.GROQ_API_KEY)
    logger.info("Groq client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    raise


# ==============================
# CHATBOT MEMORY
# ==============================
messages = []

SystemChatBot = [{
    "role": "system",
    "content": f"""You are an AI assistant helping {Username}.

When asked for code:
- Provide clean, working code directly
- Add brief comments in the code
- Give a short explanation after the code
- NO formal letter format, NO greetings, NO signatures

When asked for content:
- Write the requested content directly
- Be professional but concise
- Focus on the actual content, not formatting

Always be direct and helpful."""
}]

# ==============================
# FUNCTIONS
# ==============================

def GoogleSearch(topic: str):
    search(topic)
    return True


def ContentWriterAI(prompt: str):
    messages.append({"role": "user", "content": prompt})

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=SystemChatBot + messages,
        max_tokens=1024,
        temperature=0.7,
        top_p=1,
        stream=False
    )

    Answer = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": Answer})
    return Answer


def Content(topic: str):
    topic = topic.replace("content", "").strip()
    content_by_ai = ContentWriterAI(topic)

    os.makedirs("Data", exist_ok=True)
    file_path = os.path.join("Data", f"{topic.lower().replace(' ', '')}.txt")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content_by_ai)

    subprocess.Popen(["notepad.exe", file_path])
    return True


def YoutubeSearch(topic: str):
    url = f"https://www.youtube.com/results?search_query={topic}"
    webopen(url)
    return True


def PlayYoutube(query: str):
    playonyt(query)
    return True


def OpenApp(app, sess=requests.session()):
    app = app.lower()

    web_apps = {
        "instagram": "https://www.instagram.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://twitter.com",
        "whatsapp": "https://web.whatsapp.com",
        "youtube": "https://www.youtube.com",
        "linkedin": "https://www.linkedin.com",
        "spotify": "https://open.spotify.com",
        "netflix": "https://www.netflix.com",
        "telegram": "https://web.telegram.org",
    }

    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception:
        pass

    if app in web_apps:
        webopen(web_apps[app])
        return True

    try:
        url = f"https://www.google.com/search?q={app}"
        headers = {"User-Agent": useragent}
        response = sess.get(url, headers=headers)
        if response.status_code == 200:
            webopen(url)
            return True
    except Exception as e:
        print(f"[ERROR] While searching for {app}: {e}")

    return False


def CloseApp(app):
    try:
        app = app.lower()

        if app in ["file explorer", "explorer", "windows explorer"]:
            subprocess.run("taskkill /f /im explorer.exe", shell=True)
            subprocess.Popen("explorer.exe", shell=True)
            return True

        if "chrome" in app:
            subprocess.run("taskkill /f /im chrome.exe", shell=True)
            return True

        appclose(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        print(f"[ERROR] Could not close {app}: {e}")
        return False


def System(command: str):
    def mute(): keyboard.press_and_release("volume mute")
    def volume_up(): keyboard.press_and_release("volume up")
    def volume_down(): keyboard.press_and_release("volume down")

    if command == "mute":
        mute()
    elif command == "unmute":
        mute()  # same key toggles
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    else:
        print(f"[WARN] Unknown system command: {command}")
        return False
    return True

# ==============================
# COMMAND EXECUTION
# ==============================

async def TranslateAndExecute(commands):
    tasks = []
    for command in commands:
        cmd = command.strip().lower()
        if cmd.startswith("open "):
            tasks.append(asyncio.to_thread(OpenApp, cmd.removeprefix("open ")))
        elif cmd.startswith("close "):
            tasks.append(asyncio.to_thread(CloseApp, cmd.removeprefix("close ")))
        elif cmd.startswith("play "):
            tasks.append(asyncio.to_thread(PlayYoutube, cmd.removeprefix("play ")))
        elif cmd.startswith("content "):
            tasks.append(asyncio.to_thread(Content, cmd.removeprefix("content ")))
        elif cmd.startswith("google search "):
            tasks.append(asyncio.to_thread(GoogleSearch, cmd.removeprefix("google search ")))
        elif cmd.startswith("youtube search "):
            tasks.append(asyncio.to_thread(YoutubeSearch, cmd.removeprefix("youtube search ")))
        elif cmd.startswith("system "):
            tasks.append(asyncio.to_thread(System, cmd.removeprefix("system ")))
        else:
            print(f"[INFO] No function found for: {cmd}")

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results


async def Automation(commands):
    await TranslateAndExecute(commands)
    return True


# ==============================
# MAIN (Test examples)
# ==============================
if __name__ == "__main__":
    asyncio.run(Automation([
   
        "system volume up"
         
    ]))
