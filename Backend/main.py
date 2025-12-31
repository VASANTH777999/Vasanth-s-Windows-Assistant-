import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
import asyncio
from time import sleep
import subprocess
import threading
import json
import os
import logging

# Import centralized configuration
import config

# Setup logger
logger = logging.getLogger("VasanthAssistant.Main")

# --- Configuration from config module ---
Username = config.USERNAME
Assistantname = config.ASSISTANTNAME

DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you?'''

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

DATA_DIR = config.DATA_DIR
CHATLOG_PATH = DATA_DIR / "ChatLog.json"

# --- Helpers ---

def safe_read_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            text = f.read().strip()
            if not text:
                return []
            return json.loads(text)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def ShowDefaultChatIfNoChats():
    chats = safe_read_json(CHATLOG_PATH)
    if len(chats) < 1:
        with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
            file.write("")
        with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as file:
            file.write(DefaultMessage)


def ReadChatLogJson():
    return safe_read_json(CHATLOG_PATH)


def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        role = entry.get("role", "user")
        content = entry.get("content", "")
        if role == "user":
            formatted_chatlog += f"User: {content}\n"
        elif role == "assistant":
            formatted_chatlog += f"Assistant: {content}\n"
    formatted_chatlog = formatted_chatlog.replace("User", Username)
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname)
    with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
        file.write(AnswerModifier(formatted_chatlog))


def ShowChatsOnGUI():
    db_path = TempDirectoryPath("Database.data")
    try:
        with open(db_path, "r", encoding="utf-8") as File:
            Data = File.read()
    except FileNotFoundError:
        Data = ""

    if len(str(Data)) > 0:
        lines = Data.split("\n")
        result = "\n".join(lines)
    else:
        result = ""

    with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as File:
        File.write(result)


def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()


InitialExecution()


async def _maybe_await(func, *args, **kwargs):
    result = func(*args, **kwargs)
    if asyncio.iscoroutine(result):
        return await result
    return result


def launch_image_generation(image_query: str):
    try:
        with open(Path("Frontend") / "Files" / "ImageGeneration.data", "w", encoding="utf-8") as file:
            file.write(f"{image_query},True")
    except Exception:
        (Path("Frontend") / "Files").mkdir(parents=True, exist_ok=True)
        with open(Path("Frontend") / "Files" / "ImageGeneration.data", "w", encoding="utf-8") as file:
            file.write(f"{image_query},True")

    try:
        p1 = subprocess.Popen([
            sys.executable,
            str(Path("Backend") / "ImageGeneration.py"),
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=False)
        subprocesses.append(p1)
    except Exception as e:
        print(f"Error starting ImageGeneration.py: {e}")


def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening ...")
    Query = SpeechRecognition()
    
    # If speech recognition failed or returned None, skip this iteration
    if Query is None or not Query.strip():
        logger.warning("Speech recognition returned no valid query, skipping...")
        SetAssistantStatus("Available ...")
        SetMicrophoneStatus("False")
        return False
    
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking ...")

    Decision = FirstLayerDMM(Query)


    print("\nDecision :", Decision, "\n")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for q in Decision:
        if q.startswith("generate ") or "generate" in q:
            ImageGenerationQuery = str(q)
            ImageExecution = True

    for q in Decision:
        if not TaskExecution:
            if any(q.startswith(func) for func in Functions):
                try:
                    asyncio.run(_maybe_await(Automation, list(Decision)))
                except Exception as e:
                    print("Automation error:", e)
                TaskExecution = True

    if ImageExecution:
        launch_image_generation(ImageGenerationQuery)

    if (G and R) or R:
        SetAssistantStatus("Searching ...")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering ...")
        TextToSpeech(Answer)
        return True

    for Queries in Decision:
        if Queries.startswith("general"):
            SetAssistantStatus("Thinking ...")
            QueryFinal = Queries.replace("general ", "", 1)
            Answer = ChatBot(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering ...")
            TextToSpeech(Answer)
            return True

        elif Queries.startswith("realtime"):
            SetAssistantStatus("Searching ...")
            QueryFinal = Queries.replace("realtime ", "", 1)
            Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering ...")
            TextToSpeech(Answer)
            return True

        elif Queries.startswith("exit"):
            QueryFinal = "Okay, Bye!"
            Answer = ChatBot(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering ...")
            TextToSpeech(Answer)
            SetAssistantStatus("Shutting down ...")
            for p in subprocesses:
                try:
                    p.terminate()
                except Exception:
                    pass
            sys.exit(0)

    return False


def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            try:
                MainExecution()
            except Exception as e:
                print("Error in MainExecution:", e)
                SetAssistantStatus("Error ...")
                sleep(0.5)
        else:
            AIStatus = GetAssistantStatus()
            if "Available ..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available ...")


def SecondThread():
    GraphicalUserInterface()


if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
