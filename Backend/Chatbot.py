import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from groq import Groq
from json import load, dump
import datetime
import logging
import config

# Setup logger
logger = logging.getLogger("VasanthAssistant.Chatbot")

# Ensure Data folder exists
config.DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load configuration from config module
Username = config.USERNAME
Assistantname = config.ASSISTANTNAME

# Initialize the Groq client using the API key from config
try:
    client = Groq(api_key=config.GROQ_API_KEY)
    logger.info("Groq client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    raise

# Define a system message for the chatbot
System = f"""You are {Assistantname}, an intelligent AI assistant helping {Username}.

IMPORTANT INSTRUCTIONS:
- Give direct, concise, and accurate answers
- Be natural and conversational, not formal
- Only provide what was asked - no extra fluff
- For code: provide clean code with brief explanation, no formal letter format
- For questions: answer directly without unnecessary introduction
- Reply in English only
- Don't mention your training data or limitations
- Be helpful and precise
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# Try to load chat log or create it if it doesn't exist
chatlog_path = config.DATA_DIR / "ChatLog.json"
if not chatlog_path.exists():
    with chatlog_path.open("w") as f:
        dump([], f)

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours {minute} minutes :{second} seconds.\n"
    return data

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def ChatBot(Query, retry_count=0):
    """ This function sends the user's query to the chatbot and returns the AI's response. """
    file_path = config.DATA_DIR / "ChatLog.json"
    try:
        with file_path.open("r") as f:
            messages = load(f)
        messages.append({"role": "user", "content": f"{Query}"})
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace('</s>', '')
        messages.append({"role": "assistant", "content": Answer})
        with file_path.open("w") as f:
            dump(messages, f, indent=4)
        return AnswerModifier(Answer=Answer)
    except Exception as e:
        logger.error(f"Error in ChatBot: {e}")
        print(f"Error: {e}")
        if retry_count < 2:
            with file_path.open("w") as f:
                dump([], f, indent=4)
            return ChatBot(Query, retry_count + 1)
        else:
            return "An error occurred. Please check your configuration and try again."

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))
