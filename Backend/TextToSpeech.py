import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pygame
import random
import asyncio
import edge_tts
import os
import logging
import config

# Setup logger
logger = logging.getLogger("VasanthAssistant.TextToSpeech")

# Load voice configuration from config
AssistantVoice = config.ASSISTANT_VOICE

# Persistent asyncio loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

async def TextToAudioFile(text: str, voice: str):
    file_path = config.DATA_DIR / "speech.mp3"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists():
        file_path.unlink()
    communicate = edge_tts.Communicate(text, voice, pitch='+0Hz', rate='+15%')
    await communicate.save(str(file_path))

def TTS(text, func=lambda r=None: True):
    global AssistantVoice
    try:
        # Try to generate audio with selected voice
        try:
            loop.run_until_complete(TextToAudioFile(text, AssistantVoice))
        except Exception as e:
            # Fallback to default voice if selected voice fails
            logger.warning(f"Failed with {AssistantVoice}, falling back: {e}")
            AssistantVoice = "en-IN-PrabhatNeural"
            loop.run_until_complete(TextToAudioFile(text, AssistantVoice))

        # Play the audio
        speech_file = config.DATA_DIR / "speech.mp3"
        pygame.mixer.init()
        pygame.mixer.music.load(str(speech_file))
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if func() is False:
                break
            pygame.time.Clock().tick(10)

        return True

    except Exception as e:
        logger.error(f"Error in TTS: {e}")
        print(f"Error in TTS: {e}")
        return False

    finally:
        try:
            func(False)
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception as e:
            logger.debug(f"Error in finally block: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(". ")
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]
    if len(Data) > 4 and len(Text) > 250:
        short_text = ". ".join(Data[:2]) + ". " + random.choice(responses)
        TTS(short_text, func)
    else:
        TTS(Text, func)

if __name__ == "__main__":
    while True:
        try:
            user_input = input("Enter the text: ")
            if user_input.lower() in ["exit", "quit", "stop"]:
                print("Exiting...")
                break
            TextToSpeech(user_input)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
