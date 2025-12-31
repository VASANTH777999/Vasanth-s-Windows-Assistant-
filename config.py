"""
Vasanth's Assistant - Centralized Configuration
Loads and validates all configuration from environment variables
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())

# ============================================
# PROJECT PATHS
# ============================================
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKEND_DIR = PROJECT_ROOT / "Backend"
FRONTEND_DIR = PROJECT_ROOT / "Frontend"
DATA_DIR = PROJECT_ROOT / "Data"
TEMP_DIR = FRONTEND_DIR / "Files"
GRAPHICS_DIR = FRONTEND_DIR / "Graphics"

# ============================================
# USER CONFIGURATION
# ============================================
USERNAME = os.getenv("USERNAME", "user")
ASSISTANTNAME = os.getenv("ASSISTANTNAME", "Vasanth's Assistant")

# ============================================
# API KEYS
# ============================================
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")

# ============================================
# VOICE CONFIGURATION
# ============================================
INPUT_LANGUAGE = os.getenv("INPUT_LANGUAGE", "en")
ASSISTANT_VOICE = os.getenv("ASSISTANT_VOICE", "en-IN-PrabhatNeural")

# ============================================
# LOGGING CONFIGURATION
# ============================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# ============================================
# VALIDATION
# ============================================
def validate_configuration():
    """Validate that all required configuration is present"""
    errors = []
    warnings = []
    
    # Check API keys
    if not COHERE_API_KEY or COHERE_API_KEY == "your_cohere_api_key_here":
        errors.append("COHERE_API_KEY is not set or invalid")
    
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        errors.append("GROQ_API_KEY is not set or invalid")
    
    if not STABILITY_API_KEY or STABILITY_API_KEY == "your_stability_api_key_here":
        warnings.append("STABILITY_API_KEY is not set (image generation will not work)")
    
    return errors, warnings

def get_missing_config_message():
    """Generate helpful message for missing configuration"""
    return """
╔════════════════════════════════════════════════════════════════╗
║                  CONFIGURATION REQUIRED                        ║
╚════════════════════════════════════════════════════════════════╝

Vasanth's Assistant requires API keys to function. Please follow these steps:

1. Copy .env.example to .env:
   copy .env.example .env

2. Edit .env and add your API keys:
   
   Get Cohere API Key:
   → Visit: https://dashboard.cohere.com/api-keys
   → Sign up/login and create a new API key
   → Add to .env: COHERE_API_KEY=your_key_here
   
   Get Groq API Key:
   → Visit: https://console.groq.com/keys
   → Sign up/login and create a new API key
   → Add to .env: GROQ_API_KEY=your_key_here
   
   Get Stability AI API Key (Optional - for image generation):
   → Visit: https://platform.stability.ai/account/keys
   → Sign up/login and create a new API key
   → Add to .env: STABILITY_API_KEY=your_key_here

3. Run Solix again:
   python solix.py

For more help, see README.md
"""

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [DATA_DIR, TEMP_DIR, GRAPHICS_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_data_path(filename: str) -> Path:
    """Get path to file in Data directory"""
    return DATA_DIR / filename

def get_temp_path(filename: str) -> Path:
    """Get path to file in temp directory"""
    return TEMP_DIR / filename

def get_graphics_path(filename: str) -> Path:
    """Get path to file in graphics directory"""
    return GRAPHICS_DIR / filename

# ============================================
# EXPORT CONFIGURATION
# ============================================
__all__ = [
    'PROJECT_ROOT',
    'BACKEND_DIR',
    'FRONTEND_DIR',
    'DATA_DIR',
    'TEMP_DIR',
    'GRAPHICS_DIR',
    'USERNAME',
    'ASSISTANTNAME',
    'COHERE_API_KEY',
    'GROQ_API_KEY',
    'STABILITY_API_KEY',
    'INPUT_LANGUAGE',
    'ASSISTANT_VOICE',
    'LOG_LEVEL',
    'DEBUG_MODE',
    'validate_configuration',
    'get_missing_config_message',
    'create_directories',
    'get_data_path',
    'get_temp_path',
    'get_graphics_path',
]
