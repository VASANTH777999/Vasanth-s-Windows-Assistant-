import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from duckduckgo_search import DDGS
from json import load, dump
from groq import Groq
import datetime
import logging
import config

# Setup logger
logger = logging.getLogger("VasanthAssistant.RealtimeSearch")

# Load configuration from config module
Username = config.USERNAME
Assistantname = config.ASSISTANTNAME

# Initialize Groq client
try:
    client = Groq(api_key=config.GROQ_API_KEY)
    logger.info("Groq client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    raise

System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide answers in a professional way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Path for storing chat logs
chatlog_path = config.DATA_DIR / "ChatLog.json"
chatlog_path.parent.mkdir(exist_ok=True)

# Load or initialize chat history
if chatlog_path.exists():
    with chatlog_path.open("r") as f:
        messages = load(f)
else:
    messages = []
    with chatlog_path.open("w") as f:
        dump(messages, f)



def GoogleSearch(query):
    results = DDGS().text(query, max_results=5)
    answer = f"The search results for {query} are:\n[start]\n"
    for r in results:
        answer += f"Title: {r['title']}\nDescription: {r['body']}\nURL: {r['href']}\n\n"
    answer += "[end]"
    return answer


def AnswerModifier(answer):
    lines = answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def Information():
    now = datetime.datetime.now()
    return (
        "Use this real-time information if needed:\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds.\n"
    )

def RealtimeSearchEngine(prompt):
    global messages

    # Reload messages from file
    with chatlog_path.open("r") as f:
        messages = load(f)

    messages.append({"role": "user", "content": prompt})

    system_chatbot = [
        {"role": "system", "content": System},
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello, how can I help you?"},
        {"role": "system", "content": GoogleSearch(prompt)},
        {"role": "system", "content": Information()}
    ]

    try:
        completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",# replace with a Groq available model
            messages=system_chatbot + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=False
        )
    except Exception as e:
        return f"Error during completion: {e}"

    # Extract response
    try:
        Answer = completion.choices[0].message.content
    except Exception:
        Answer = ""

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    with chatlog_path.open("w") as f:
        dump(messages, f, indent=4)

    return AnswerModifier(Answer)

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query (type 'exit' to stop): ")
        if prompt.lower() == "exit":
            break
        response = RealtimeSearchEngine(prompt)
        print(response)

