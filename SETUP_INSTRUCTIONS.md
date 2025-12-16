# Setup Instructions

## Python Installation Issue Detected

Python is not properly installed on your system. The Windows Store alias is blocking Python commands.

## Solution Options:

### Option 1: Install Python (Recommended)
1. Download Python from: https://www.python.org/downloads/
2. **IMPORTANT**: During installation, check ✅ "Add Python to PATH"
3. Choose "Install Now" (not "Customize installation")
4. After installation, restart your terminal/PowerShell
5. Verify: `python --version`

### Option 2: Use Anaconda/Miniconda (If you have it)
If you have Anaconda installed:
```powershell
conda create -n nancy python=3.11
conda activate nancy
pip install -r requirements.txt
python app.py
```

### Option 3: Disable Windows Store Python Alias
1. Open Windows Settings
2. Go to Apps → Advanced app settings → App execution aliases
3. Turn OFF the toggles for `python.exe` and `python3.exe`
4. Then install Python from python.org

## After Python is Installed:

```powershell
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Open browser to:
# http://localhost:5000
```

## Quick Test:
Run this to verify Python works:
```powershell
python --version
```







