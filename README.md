# 🤖 Vasanth's Assistant

**Voice-Activated AI Desktop Assistant for Windows**

Vasanth's Assistant is a powerful, production-ready AI assistant that combines voice recognition, natural language processing, automation, and real-time web search capabilities into a beautiful PyQt5 interface.

---

## ✨ Features

- 🎤 **Voice Recognition** - Natural speech-to-text using Web Speech API
- 🗣️ **Text-to-Speech** - High-quality voice synthesis with Microsoft Edge TTS
- 💬 **Conversational AI** - Context-aware chatbot powered by Groq Llama 3.3
- 🔍 **Real-time Search** - Web search integration with DuckDuckGo
- 🖥️ **System Automation** - Open/close apps, control volume, manage windows
- 🌐 **Web Automation** - Google/YouTube search, play videos
- ✍️ **Content Generation** - AI-powered content writing
- 🎨 **Image Generation** - Create AI images with Stability AI
- 📊 **Modern GUI** - Beautiful PyQt5 interface with animations
- 💾 **Chat History** - Persistent conversation memory

---

## 📋 System Requirements

- **Operating System:** Windows 10/11
- **Python:** 3.8 or higher
- **Google Chrome:** Required for speech recognition
- **Internet Connection:** Required for AI services

---

## 🚀 Quick Start

### 1. Clone or Download the Project

```bash
git clone https://github.com/VASANTH777999/Vasanth-s-Windows-Assistant-.git
```

```bash
cd Vasanth-s-Window-Assistant
```
### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required API Keys
COHERE_API_KEY="your_cohere_api_key_here"
GROQ_API_KEY="your_groq_api_key_here"
STABILITY_API_KEY="your_stability_api_key_here"

# User Configuration
USERNAME=your_name
ASSISTANTNAME=Vasanth's Assistant

# Voice Settings
INPUT_LANGUAGE=en
ASSISTANT_VOICE=en-IN-PrabhatNeural
```

### 4. Get API Keys

#### Cohere API (Required)
1. Visit [https://dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys)
2. Sign up or log in
3. Create a new API key
4. Copy and paste into `.env`

#### Groq API (Required)
1. Visit [https://console.groq.com/keys](https://console.groq.com/keys)
2. Sign up or log in
3. Create a new API key
4. Copy and paste into `.env`

#### Stability AI (Optional - for image generation)
1. Visit [https://platform.stability.ai/account/keys](https://platform.stability.ai/account/keys)
2. Sign up or log in
3. Create a new API key
4. Copy and paste into `.env`

### 5. Launch Vasanth's Assistant

```bash
python Vasanth'sAI.py
```

That's it! Vasanth's Assistant will validate your configuration and launch the GUI.

---

## 🎯 Usage

### Voice Commands

Click the microphone icon to activate voice recognition, then speak your command:

**General Conversation:**
- "How are you?"
- "Tell me about Python programming"
- "What's the weather like?" (requires real-time search)

**Web Search:**
- "Search for artificial intelligence on Google"
- "Search for Python tutorials on YouTube"

**Automation:**
- "Open Chrome"
- "Close Notepad"
- "Play Despacito on YouTube"

**System Control:**
- "Volume up"
- "Volume down"
- "Mute"

**Content Creation:**
- "Write a professional email about project updates"
- "Generate content about machine learning"

**Image Generation:**
- "Generate image of a sunset over mountains"
- "Create an image of a futuristic city"

### GUI Navigation

- **Home Tab:** Main voice interaction screen with animated assistant
- **Chat Tab:** View full conversation history
- **Microphone Button:** Toggle voice recognition on/off
- **Status Indicator:** Shows current assistant activity

---

## 📁 Project Structure

```
Akshay/
├── Vasanth'sAI.py           # Main entry point (run this!)
├── config.py                # Centralized configuration
├── requirements.txt         # Python dependencies
├── .env                     # Your API keys (create from .env.example)
├── README.md                # This file
│
├── Backend/                 # Core AI and automation modules
│   ├── main.py              # Application orchestrator
│   ├── Model.py             # Query classification (Cohere)
│   ├── Chatbot.py           # Conversational AI (Groq)
│   ├── Automation.py        # Task automation
│   ├── SpeechToText.py      # Voice recognition
│   ├── TextToSpeech.py      # Voice synthesis
│   ├── RealtimeSearchEngine.py  # Web search
│   └── ImageGeneration.py   # AI image creation
│
├── Frontend/                # User interface
│   ├── GUI.PY               # PyQt5 interface
│   ├── Files/               # Runtime data
│   └── Graphics/            # UI assets (icons, animations)
│
└── Data/                    # Generated data and logs
    ├── ChatLog.json         # Conversation history
    ├── speech.mp3           # Generated audio
    ├── logs/                # Application logs
    └── *.txt                # Generated content files
```

---

## ⚙️ Configuration

### Environment Variables

Edit `.env` to customize Vasanth's Assistant:

| Variable | Description | Default |
|----------|-------------|---------|
| `USERNAME` | Your name | user |
| `ASSISTANTNAME` | Assistant's name | Vasanth's Assistant |
| `INPUT_LANGUAGE` | Speech recognition language | en |
| `ASSISTANT_VOICE` | Text-to-speech voice | en-IN-PrabhatNeural |
| `LOG_LEVEL` | Logging verbosity | INFO |
| `DEBUG_MODE` | Enable debug output | false |

### Available Voices

- `en-US-AriaNeural` - US English Female
- `en-US-GuyNeural` - US English Male
- `en-IN-PrabhatNeural` - Indian English Male (default)
- `en-IN-NeerjaNeural` - Indian English Female
- `en-GB-SoniaNeural` - British English Female

### Supported Languages

Speech recognition supports 100+ languages. Common examples:
- `en` - English
- `hi` - Hindi
- `es` - Spanish
- `fr` - French
- `de` - German
- `ja` - Japanese

---

## 🐛 Troubleshooting

### "Missing required packages"
```bash
pip install -r requirements.txt
```

### "COHERE_API_KEY is not set"
- Make sure you've created `.env` from `.env.example`
- Verify your API keys are correctly pasted (no extra spaces)
- Check that `.env` is in the project root directory

### "Chrome not detected"
- Install Google Chrome from [google.com/chrome](https://www.google.com/chrome/)
- Restart your computer after installation

### "Failed to initialize Chrome WebDriver"
- Ensure Chrome is up to date
- Check your internet connection (ChromeDriver downloads automatically)
- Try running as administrator

### Voice recognition not working
- Grant microphone permissions when prompted
- Check that your microphone is working in other applications
- Try restarting Vasanth's Assistant

### No audio output
- Check your system volume
- Verify speakers/headphones are connected
- Check `Data/speech.mp3` is being created

### Application crashes on startup
- Check logs in `Data/logs/vasanth_assistant.log`
- Verify all API keys are valid
- Try deleting `Data/ChatLog.json` and restarting

---

## 📊 Logs and Data

### Log Files
Application logs are stored in `Data/logs/vasanth_assistant.log`

To view recent logs:
```bash
type Data\logs\Vasanth_assistant.log
```

### Chat History
Conversation history is saved in `Data/ChatLog.json`

To clear chat history:
```bash
del Data\ChatLog.json
```

### Generated Content
- Text content: `Data/*.txt`
- Generated images: `Data/*.png`
- Audio files: `Data/speech.mp3`

---

## 🔒 Security Notes

- **Never commit `.env` to version control** - It contains your API keys
- API keys are loaded from environment variables (not hardcoded)
- Keep your API keys private and rotate them regularly
- Monitor your API usage to avoid unexpected charges

---

## 🛠️ Development

### Running in Debug Mode

Edit `.env`:
```env
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

Then run:
```bash
python Vasanth'sAI.py
```

### Project Dependencies

Core libraries:
- **PyQt5** - GUI framework
- **cohere** - Query classification
- **groq** - LLM inference
- **selenium** - Browser automation
- **edge-tts** - Text-to-speech
- **pygame** - Audio playback
- **duckduckgo-search** - Web search

See `requirements.txt` for complete list.

---

## 📝 License

This project is for educational and personal use.

---

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in `Data/logs/solix.log`
3. Verify your configuration in `.env`

---

## 🎉 Enjoy Vasanth's Assistant!

Launch with:
```bash
python solix.py
```

**Made with ❤️ for Vasanth**

