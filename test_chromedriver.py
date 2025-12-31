"""
Test script to download and verify ChromeDriver
"""
import sys
from pathlib import Path
import requests
import zipfile
import io

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import config

def download_chromedriver():
    """Download ChromeDriver for win64"""
    arch = 'win64'
    
    # Try multiple versions (prioritize 143 to match current Chrome)
    versions = [
        '143.0.7499.170',  # Match current Chrome version
        '143.0.7499.169',
        '143.0.7499.0',
        '131.0.6778.204',
        '130.0.6723.116',
        '129.0.6668.100',
        '128.0.6613.137',
    ]
    
    driver_path = config.DATA_DIR / "chromedriver"
    driver_path.mkdir(parents=True, exist_ok=True)
    driver_exe = driver_path / "chromedriver.exe"
    
    if driver_exe.exists():
        print(f"[OK] ChromeDriver already exists at: {driver_exe}")
        return str(driver_exe)
    
    print(f"Downloading ChromeDriver for {arch}...")
    
    for version in versions:
        url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/{arch}/chromedriver-{arch}.zip"
        print(f"\nTrying: {url}")
        
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                print(f"[OK] Downloaded successfully ({len(response.content)} bytes)")
                
                # Extract zip
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                    print(f"Files in zip: {zip_ref.namelist()}")
                    
                    # Find chromedriver.exe
                    for file_info in zip_ref.filelist:
                        if file_info.filename.endswith('chromedriver.exe'):
                            print(f"Extracting: {file_info.filename}")
                            with zip_ref.open(file_info) as source:
                                with driver_exe.open('wb') as target:
                                    target.write(source.read())
                            print(f"[OK] ChromeDriver extracted to: {driver_exe}")
                            print(f"[OK] File size: {driver_exe.stat().st_size} bytes")
                            return str(driver_exe)
                
                print("[ERROR] No chromedriver.exe found in zip")
            else:
                print(f"[ERROR] HTTP {response.status_code}")
        except Exception as e:
            print(f"[ERROR] {e}")
    
    print("\n[ERROR] Failed to download from all sources")
    return None

if __name__ == "__main__":
    print("="*60)
    print("ChromeDriver Download Test")
    print("="*60 + "\n")
    
    result = download_chromedriver()
    
    if result:
        print(f"\n{'='*60}")
        print("[SUCCESS] ChromeDriver is ready!")
        print(f"Location: {result}")
        print("="*60)
    else:
        print(f"\n{'='*60}")
        print("[FAILED] Could not download ChromeDriver")
        print("="*60)
