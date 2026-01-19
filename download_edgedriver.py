"""
EdgeDriver Downloader
Downloads the correct EdgeDriver version matching your Edge browser
"""

import os
import sys
import subprocess
import zipfile
import shutil
from pathlib import Path

def get_edge_version():
    """Get installed Edge browser version"""
    try:
        result = subprocess.run(
            ['powershell', '-Command',
             "(Get-Item 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe').VersionInfo.ProductVersion"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print(f"Edge browser version: {version}")
        return version
    except Exception as e:
        print(f"Error getting Edge version: {e}")
        return None

def download_edgedriver(version):
    """Download EdgeDriver using PowerShell"""
    url = f"https://msedgedriver.azureedge.net/{version}/edgedriver_win64.zip"
    output_file = "edgedriver_temp.zip"

    print(f"Downloading EdgeDriver from: {url}")

    # Use PowerShell with ProgressPreference to avoid timeout issues
    ps_command = f"""
    $ProgressPreference = 'SilentlyContinue'
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri '{url}' -OutFile '{output_file}' -UseBasicParsing
    """

    try:
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True,
            text=True,
            check=True,
            timeout=120
        )

        if os.path.exists(output_file):
            print(f"Download successful: {output_file}")
            return output_file
        else:
            print("Download failed - file not found")
            return None
    except subprocess.TimeoutExpired:
        print("Download timed out after 120 seconds")
        return None
    except Exception as e:
        print(f"Error downloading EdgeDriver: {e}")
        if hasattr(e, 'stderr'):
            print(f"Error details: {e.stderr}")
        return None

def extract_edgedriver(zip_file, extract_to="edgedriver_win64"):
    """Extract EdgeDriver from zip file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(extract_to, exist_ok=True)

        # Backup old driver if exists
        old_driver = os.path.join(extract_to, "msedgedriver.exe")
        if os.path.exists(old_driver):
            backup = os.path.join(extract_to, "msedgedriver_old.exe")
            print(f"Backing up old driver to: {backup}")
            shutil.move(old_driver, backup)

        # Extract new driver
        print(f"Extracting EdgeDriver to: {extract_to}")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

        # Verify extraction
        new_driver = os.path.join(extract_to, "msedgedriver.exe")
        if os.path.exists(new_driver):
            print(f"EdgeDriver successfully installed at: {new_driver}")
            return True
        else:
            print("Extraction failed - driver not found")
            return False

    except Exception as e:
        print(f"Error extracting EdgeDriver: {e}")
        return False
    finally:
        # Clean up zip file
        if os.path.exists(zip_file):
            os.remove(zip_file)
            print(f"Cleaned up: {zip_file}")

def main():
    """Main function"""
    print("=" * 60)
    print("EdgeDriver Downloader for Facebook Warmup Bot")
    print("=" * 60)
    print()

    # Get Edge version
    version = get_edge_version()
    if not version:
        print("Failed to detect Edge browser version")
        return 1

    print()

    # Download EdgeDriver
    zip_file = download_edgedriver(version)
    if not zip_file:
        print("\nFailed to download EdgeDriver")
        print("\nManual Download Instructions:")
        print(f"1. Visit: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
        print(f"2. Download EdgeDriver for version: {version}")
        print(f"3. Extract to: edgedriver_win64/")
        return 1

    print()

    # Extract EdgeDriver
    if extract_edgedriver(zip_file):
        print()
        print("=" * 60)
        print("SUCCESS! EdgeDriver is ready to use")
        print("=" * 60)
        return 0
    else:
        print("\nFailed to extract EdgeDriver")
        return 1

if __name__ == "__main__":
    sys.exit(main())
