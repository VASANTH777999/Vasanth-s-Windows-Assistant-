import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import os
import requests
from io import BytesIO
from PIL import Image
import logging
import config

# Setup logger
logger = logging.getLogger("VasanthAssistant.ImageGeneration")

# ---------------- CONFIG ----------------
DATA_FOLDER = config.DATA_DIR
if not DATA_FOLDER.exists():
    DATA_FOLDER.mkdir(parents=True)

STABILITY_API_KEY = config.STABILITY_API_KEY
STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

HEADERS = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    "Accept": "image/*"  # Expect image in response
}

# ---------------- UTILITIES ----------------
def save_and_open_image(image_bytes, prompt):
    filename = DATA_FOLDER / f"{prompt[:20].replace(' ', '_')}.png"
    with filename.open("wb") as f:
        f.write(image_bytes)
    logger.info(f"Image saved at {filename}")
    print(f"[+] Image saved at {filename}")
    img = Image.open(BytesIO(image_bytes))
    img.show()

# ---------------- GENERATOR ----------------
def generate_image_stability(prompt: str):
    try:
        payload = {
            "prompt": prompt,
            "output_format": "png"
        }
        response = requests.post(STABILITY_API_URL, headers=HEADERS, files={"none": ''}, data=payload)

        if response.status_code == 200:
            save_and_open_image(response.content, prompt)
        else:
            error_msg = f"Stability API Error: {response.text}"
            logger.error(error_msg)
            print(error_msg)
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        print(f"Error generating image: {e}")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    while True:
        user_prompt = input("Enter prompt (or 'quit'): ")
        if user_prompt.lower() == "quit":
            break
        generate_image_stability(user_prompt)
