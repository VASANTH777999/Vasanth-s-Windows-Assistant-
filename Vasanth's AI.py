"""
╔════════════════════════════════════════════════════════════════╗
║                 VASANTH'S ASSISTANT                             ║
║              Voice-Activated AI Desktop Assistant              ║
╚════════════════════════════════════════════════════════════════╝

Main Entry Point - Launch with: python solix.py
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

def check_python_version():
    """Ensure Python 3.8+ is being used"""
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8 or higher is required")
        print(f"        Current version: {sys.version}")
        print("        Please upgrade Python and try again")
        sys.exit(1)

def check_dependencies():
    """Check if required packages are installed"""
    missing_packages = []
    required_packages = {
        'PyQt5': 'PyQt5',
        'cohere': 'cohere',
        'groq': 'groq',
        'edge_tts': 'edge-tts',
        'selenium': 'selenium',
        'pywhatkit': 'pywhatkit',
        'pygame': 'pygame',
        'dotenv': 'python-dotenv',
        'requests': 'requests',
    }
    
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("[ERROR] Missing required packages. Please install dependencies:")
        print(f"\n        pip install -r requirements.txt\n")
        print("        Missing packages:")
        for pkg in missing_packages:
            print(f"        - {pkg}")
        sys.exit(1)

def check_chrome():
    """Check if Chrome is available for speech recognition"""
    try:
        import shutil
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        
        chrome_found = any(os.path.exists(path) for path in chrome_paths)
        if not chrome_found:
            chrome_found = shutil.which("chrome") is not None or shutil.which("google-chrome") is not None
        
        if not chrome_found:
            print("[WARNING] Google Chrome not detected")
            print("          Speech recognition requires Chrome to be installed")
            print("          Download from: https://www.google.com/chrome/")
            print("\n          Continuing anyway... (speech features may not work)\n")
    except Exception:
        pass

def setup_configuration():
    """Setup and validate configuration"""
    import config
    
    # Create necessary directories
    config.create_directories()
    
    # Check if .env file exists
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        print("[WARNING] Configuration file (.env) not found!")
        print(config.get_missing_config_message())
        
        response = input("\nDo you want to create .env file now? (y/n): ").strip().lower()
        if response == 'y':
            example_file = PROJECT_ROOT / ".env.example"
            if example_file.exists():
                import shutil
                shutil.copy(example_file, env_file)
                print(f"\n[OK] Created .env file at: {env_file}")
                print("     Please edit this file and add your API keys, then run solix.py again")
            else:
                print("[ERROR] .env.example not found. Please create .env manually")
        sys.exit(0)
    
    # Validate configuration
    errors, warnings = config.validate_configuration()
    
    if errors:
        print("[ERROR] Configuration Errors:")
        for error in errors:
            print(f"        - {error}")
        print(config.get_missing_config_message())
        sys.exit(1)
    
    if warnings:
        print("[WARNING] Configuration Warnings:")
        for warning in warnings:
            print(f"          - {warning}")
        print()

def setup_logging():
    """Setup logging system"""
    import logging
    import config
    
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    
    # Create logs directory
    logs_dir = config.DATA_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / "vasanth_assistant.log"),
            logging.StreamHandler(sys.stdout) if config.DEBUG_MODE else logging.NullHandler()
        ]
    )
    
    return logging.getLogger("VasanthAssistant")

def main():
    """Main entry point"""
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        except:
            pass  # Fallback to default encoding
    
    print("\n" + "="*64)
    print("  VASANTH'S ASSISTANT")
    print("="*64 + "\n")
    
    # Step 1: Check Python version
    print("[*] Checking Python version...")
    check_python_version()
    print("    [OK] Python version OK\n")
    
    # Step 2: Check dependencies
    print("[*] Checking dependencies...")
    check_dependencies()
    print("    [OK] All dependencies installed\n")
    
    # Step 3: Check Chrome
    print("[*] Checking for Google Chrome...")
    check_chrome()
    
    # Step 4: Setup configuration
    print("[*] Loading configuration...")
    setup_configuration()
    print("    [OK] Configuration loaded\n")
    
    # Step 5: Setup logging
    print("[*] Setting up logging...")
    logger = setup_logging()
    print("    [OK] Logging configured\n")
    
    # Step 6: Launch application
    print("[*] Launching Vasanth's Assistant...\n")
    print("="*64 + "\n")
    
    try:
        # Import and run main application
        from Backend.main import FirstThread, SecondThread
        import threading
        
        logger.info("Starting Vasanth's Assistant")
        
        # Start voice processing thread
        voice_thread = threading.Thread(target=FirstThread, daemon=True)
        voice_thread.start()
        logger.info("Voice processing thread started")
        
        # Start GUI (blocking)
        logger.info("Starting GUI")
        SecondThread()
        
    except KeyboardInterrupt:
        print("\n\n[STOP] Shutting down Vasanth's Assistant...")
        logger.info("Shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Fatal Error: {e}")
        logger.exception("Fatal error occurred")
        print("\nPlease check the logs for more details:")
        print(f"   {PROJECT_ROOT / 'Data' / 'logs' / 'vasanth_assistant.log'}")
        sys.exit(1)

if __name__ == "__main__":
    main()
