# Facebook Warmup Bot - Web Interface

A web-based interface to manage multiple Facebook accounts and run warmup tasks sequentially.

## Features

- ✅ Add multiple Edge profile paths
- ✅ Select profiles with checkboxes
- ✅ Run bot sequentially on selected profiles
- ✅ Real-time status updates
- ✅ Live log console
- ✅ Auto-uncheck completed profiles

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Edge WebDriver

Make sure you have the Edge WebDriver in the correct location:
```
fb_warmup_app/
├── edgedriver_win64/
│   └── msedgedriver.exe
├── app.py
├── facebook_bot.py
└── ...
```

Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/

### 3. Run the Server

```bash
python app.py
```

### 4. Open Browser

Navigate to: **http://localhost:5000**

## Usage

### Adding Profiles

1. Enter a **Profile Name** (e.g., "Account 1")
2. Enter the **Edge Profile Path**:
   - Default: `C:\Users\YOUR_USERNAME\AppData\Local\Microsoft\Edge\User Data`
   - For multiple profiles, use different Edge profiles

### Finding Your Edge Profile Path

1. Open Edge browser
2. Go to `edge://version`
3. Look for "Profile Path"
4. Use the parent folder (User Data)

### Running the Bot

1. ✅ Check the profiles you want to run
2. Click **"Run Selected"**
3. Watch the progress in real-time
4. Profiles auto-uncheck when completed

## File Structure

```
fb_warmup_app/
├── app.py              # Flask backend server
├── facebook_bot.py     # Bot class module
├── requirements.txt    # Python dependencies
├── profiles.json       # Saved profiles (auto-created)
├── templates/
│   └── index.html      # Web interface
├── edgedriver_win64/
│   └── msedgedriver.exe
├── warmupss/           # Screenshots folder
└── temp_images/        # Downloaded images folder
```

## Tasks Performed

For each profile, the bot will:

1. 🌐 Setup browser with profile
2. 🔐 Verify login status
3. 📰 Check feed access
4. 👤 Visit first post author's profile
5. 📖 Watch & like first story
6. ❤️ Like first post
7. 💬 Comment on first post
8. 📷 Create image post (from Pexels)

## Notes

- Close ALL Edge windows before running
- Each profile = One Facebook account
- Bot runs sequentially (one at a time)
- 5-second delay between profiles
- Screenshots saved to `warmupss/` folder

## Troubleshooting

### "Edge driver not found"
- Download the correct version from Microsoft
- Place in `edgedriver_win64/` folder

### "Not logged in"
- Open Edge with that profile manually
- Login to Facebook and save credentials
- Close Edge completely

### Bot stuck
- Click "Stop" button
- Wait for current profile to finish
- Restart the server if needed
# fb_warmup_bot
