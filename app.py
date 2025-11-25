"""
Facebook Warmup Bot - Flask Backend
Manages multiple Edge profiles and runs bot sequentially
Dashboard runs on Chrome, automation uses Edge profiles
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading
import json
import os
import time
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Store profiles and status
PROFILES_FILE = "profiles.json"
bot_status = {
    "running": False,
    "stop_requested": False,
    "current_profile": None,
    "current_task": None,
    "current_round": 0,
    "total_rounds": 1,
    "queue": [],           # List of {"profile": name, "round": num, "status": "pending/running/completed/failed"}
    "current_queue_index": -1,
    "completed": [],
    "failed": [],
    "logs": [],
    "task_results": {}
}

def load_profiles():
    """Load profiles from JSON file"""
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_profiles(profiles):
    """Save profiles to JSON file"""
    with open(PROFILES_FILE, 'w') as f:
        json.dump(profiles, f, indent=2)

def add_log(message, level="INFO"):
    """Add log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    bot_status["logs"].append(log_entry)
    # Keep only last 200 logs
    if len(bot_status["logs"]) > 200:
        bot_status["logs"] = bot_status["logs"][-200:]
    print(log_entry)

def run_bot_on_profile(profile, round_num, queue_index):
    """Run the warmup bot on a single profile"""
    from facebook_bot import FacebookWarmupBot
    
    profile_round_key = f"{profile['name']}_R{round_num}"
    
    add_log(f"Starting bot for: {profile['name']} (Round {round_num})")
    bot_status["current_profile"] = profile['name']
    bot_status["current_round"] = round_num
    bot_status["current_queue_index"] = queue_index
    bot_status["queue"][queue_index]["status"] = "running"
    bot_status["task_results"][profile_round_key] = {}
    
    # Default Pexels API key
    PEXELS_API_KEY = "BpDFCOtx2UgT1vQF6KhXwecY5dLq8qiOjLkHWyqLgmBy1iX0gDIbVFPX"
    
    bot = FacebookWarmupBot(
        profile_path=profile['path'],
        pexels_api_key=PEXELS_API_KEY
    )
    
    results = {
        "profile": profile['name'],
        "round": round_num,
        "tasks": {}
    }
    
    try:
        # Check for stop request
        if bot_status["stop_requested"]:
            add_log("Stop requested - skipping profile", "WARNING")
            bot_status["queue"][queue_index]["status"] = "skipped"
            return results
        
        # Task 1: Setup Browser
        bot_status["current_task"] = "Setting up browser"
        add_log("Setting up Edge browser...")
        if not bot.setup_browser():
            raise Exception("Failed to setup browser")
        results["tasks"]["browser_setup"] = True
        add_log("Browser setup: SUCCESS", "SUCCESS")
        time.sleep(3)
        
        # Check for stop request
        if bot_status["stop_requested"]:
            add_log("Stop requested - closing browser", "WARNING")
            bot.close_browser()
            bot_status["queue"][queue_index]["status"] = "skipped"
            return results
        
        # Task 2: Navigate to Facebook
        bot_status["current_task"] = "Navigating to Facebook"
        add_log("Navigating to Facebook...")
        if not bot.navigate_to_facebook():
            raise Exception("Failed to navigate to Facebook")
        results["tasks"]["navigation"] = True
        add_log("Navigation: SUCCESS", "SUCCESS")
        time.sleep(3)
        
        # Task 3: Check Login
        bot_status["current_task"] = "Checking login status"
        add_log("Checking login status...")
        if not bot.check_login_status():
            raise Exception("Not logged in - please login to this profile first")
        results["tasks"]["login_check"] = True
        add_log("Login check: SUCCESS - User is logged in", "SUCCESS")
        
        # Task 4: Verify Feed
        bot_status["current_task"] = "Verifying feed access"
        add_log("Verifying feed access...")
        feed_ok = bot.verify_feed_access()
        results["tasks"]["feed_access"] = feed_ok
        if feed_ok:
            add_log("Feed access: SUCCESS", "SUCCESS")
        else:
            add_log("Feed access: LIMITED", "WARNING")
        
        # Check for stop request
        if bot_status["stop_requested"]:
            add_log("Stop requested - stopping tasks", "WARNING")
            bot.close_browser()
            bot_status["queue"][queue_index]["status"] = "skipped"
            return results
        
        # Task 5: Browse Feed
        bot_status["current_task"] = "Browsing feed"
        add_log("Browsing feed...")
        bot.scroll_page()
        bot.random_delay(2, 3)
        bot.scroll_page()
        results["tasks"]["browse_feed"] = True
        add_log("Feed browsing: SUCCESS", "SUCCESS")
        
        # Task 6: Visit Profile
        bot_status["current_task"] = "Visiting profile"
        add_log("Visiting first post author's profile...")
        profile_visit = bot.visit_first_post_profile()
        results["tasks"]["visit_profile"] = profile_visit
        if profile_visit:
            add_log("Profile visit: SUCCESS", "SUCCESS")
        else:
            add_log("Profile visit: SKIPPED", "WARNING")
        bot.random_delay(3, 5)
        
        # Task 7: Return Home
        bot_status["current_task"] = "Returning home"
        add_log("Returning to home feed...")
        home_return = bot.go_back_to_home()
        results["tasks"]["return_home"] = home_return
        if home_return:
            add_log("Return home: SUCCESS", "SUCCESS")
        else:
            add_log("Return home: FAILED", "WARNING")
        bot.random_delay(3, 5)
        
        # Check for stop request
        if bot_status["stop_requested"]:
            add_log("Stop requested - stopping tasks", "WARNING")
            bot.close_browser()
            bot_status["queue"][queue_index]["status"] = "skipped"
            return results
        
        # Task 8: Watch and Like Story
        bot_status["current_task"] = "Watching story"
        add_log("Watching and liking story...")
        story_ok = bot.watch_and_like_first_story()
        results["tasks"]["story"] = story_ok
        if story_ok:
            add_log("Story watch/like: SUCCESS", "SUCCESS")
        else:
            add_log("Story watch/like: SKIPPED (no stories available)", "WARNING")
        bot.random_delay(3, 5)
        
        # Task 9: Like Post
        bot_status["current_task"] = "Liking post"
        add_log("Liking first post...")
        try:
            bot.driver.execute_script("window.scrollTo(0, 0);")
        except:
            pass
        bot.random_delay(2, 3)
        like_ok = bot.like_first_post()
        results["tasks"]["like_post"] = like_ok
        if like_ok:
            add_log("Post like: SUCCESS", "SUCCESS")
        else:
            add_log("Post like: SKIPPED", "WARNING")
        bot.random_delay(3, 5)
        
        # Check for stop request
        if bot_status["stop_requested"]:
            add_log("Stop requested - stopping tasks", "WARNING")
            bot.close_browser()
            bot_status["queue"][queue_index]["status"] = "skipped"
            return results
        
        # Task 10: Comment on Post
        bot_status["current_task"] = "Commenting on post"
        add_log("Commenting on first post...")
        comment_ok = bot.comment_on_first_post()
        results["tasks"]["comment"] = comment_ok
        if comment_ok:
            add_log("Comment: SUCCESS", "SUCCESS")
        else:
            add_log("Comment: SKIPPED", "WARNING")
        bot.random_delay(3, 5)
        
        # Task 11: Create Image Post
        bot_status["current_task"] = "Creating image post"
        add_log("Creating image post...")
        post_ok = bot.create_image_post()
        results["tasks"]["image_post"] = post_ok
        if post_ok:
            add_log("Image post: SUCCESS", "SUCCESS")
        else:
            add_log("Image post: FAILED", "WARNING")
        
        # All tasks completed successfully
        bot_status["queue"][queue_index]["status"] = "completed"
        bot_status["completed"].append(profile_round_key)
        add_log(f"ALL TASKS COMPLETED for {profile['name']} (Round {round_num})", "SUCCESS")
        bot_status["task_results"][profile_round_key] = results["tasks"]
        
    except Exception as e:
        add_log(f"ERROR for {profile['name']} (Round {round_num}): {str(e)}", "ERROR")
        results["error"] = str(e)
        bot_status["queue"][queue_index]["status"] = "failed"
        bot_status["failed"].append(profile_round_key)
    
    finally:
        bot_status["current_task"] = "Closing browser"
        add_log("Closing browser...")
        try:
            bot.close_browser()
        except:
            pass
        time.sleep(2)
    
    return results

def run_bot_sequential(selected_profiles, loops=1):
    """Run bot on multiple profiles sequentially with multiple rounds using queue system"""
    global bot_status
    
    bot_status["running"] = True
    bot_status["stop_requested"] = False
    bot_status["completed"] = []
    bot_status["failed"] = []
    bot_status["logs"] = []
    bot_status["task_results"] = {}
    bot_status["current_round"] = 0
    bot_status["total_rounds"] = loops
    bot_status["current_queue_index"] = -1
    
    # Build the queue - all profiles for all rounds
    queue = []
    for round_num in range(1, loops + 1):
        for profile_name in selected_profiles:
            queue.append({
                "profile": profile_name,
                "round": round_num,
                "status": "pending"  # pending, running, completed, failed, skipped
            })
    
    bot_status["queue"] = queue
    
    profiles = load_profiles()
    profiles_dict = {p['name']: p for p in profiles}
    
    total_tasks = len(queue)
    
    add_log("="*50)
    add_log(f"STARTING WARMUP QUEUE: {len(selected_profiles)} PROFILE(S) x {loops} ROUND(S) = {total_tasks} TASKS")
    add_log("="*50)
    add_log("Dashboard: Chrome | Automation: Edge")
    add_log("="*50)
    
    # Display queue
    add_log("")
    add_log("QUEUE:")
    for i, item in enumerate(queue):
        add_log(f"  {i+1}. {item['profile']} - Round {item['round']}")
    add_log("")
    
    # Process queue
    for index, queue_item in enumerate(queue):
        if bot_status["stop_requested"]:
            add_log("STOP REQUESTED - Marking remaining tasks as skipped", "WARNING")
            for remaining_index in range(index, len(queue)):
                if bot_status["queue"][remaining_index]["status"] == "pending":
                    bot_status["queue"][remaining_index]["status"] = "skipped"
            break
        
        profile_name = queue_item["profile"]
        round_num = queue_item["round"]
        
        if profile_name not in profiles_dict:
            add_log(f"Profile '{profile_name}' not found - skipping", "WARNING")
            bot_status["queue"][index]["status"] = "skipped"
            continue
        
        profile = profiles_dict[profile_name]
        
        add_log("")
        add_log("="*50)
        add_log(f"TASK {index + 1}/{total_tasks}: {profile_name} (Round {round_num}/{loops})")
        add_log("="*50)
        
        run_bot_on_profile(profile, round_num, index)
        
        # Check if more tasks to process
        if index < total_tasks - 1 and not bot_status["stop_requested"]:
            add_log("Waiting 5 seconds before next task...")
            time.sleep(5)
    
    # Calculate final stats
    completed_count = len([q for q in bot_status["queue"] if q["status"] == "completed"])
    failed_count = len([q for q in bot_status["queue"] if q["status"] == "failed"])
    skipped_count = len([q for q in bot_status["queue"] if q["status"] == "skipped"])
    
    bot_status["running"] = False
    bot_status["current_profile"] = None
    bot_status["current_task"] = None
    bot_status["current_round"] = 0
    bot_status["current_queue_index"] = -1
    
    add_log("")
    add_log("="*50)
    add_log("QUEUE COMPLETED!")
    add_log(f"Total Tasks: {total_tasks}")
    add_log(f"Completed: {completed_count} | Failed: {failed_count} | Skipped: {skipped_count}")
    add_log("="*50)

# ============ ROUTES ============

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """Get all profiles"""
    profiles = load_profiles()
    return jsonify(profiles)

@app.route('/api/profiles', methods=['POST'])
def add_profile():
    """Add a new profile"""
    data = request.json
    profiles = load_profiles()
    
    # Check for duplicate
    for p in profiles:
        if p['path'] == data['path']:
            return jsonify({"error": "Profile path already exists"}), 400
    
    # Generate unique ID
    max_id = max([p['id'] for p in profiles], default=0)
    
    new_profile = {
        "id": max_id + 1,
        "name": data['name'],
        "path": data['path'],
        "created": datetime.now().isoformat()
    }
    
    profiles.append(new_profile)
    save_profiles(profiles)
    
    return jsonify(new_profile)

@app.route('/api/profiles/<int:profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    """Delete a profile"""
    profiles = load_profiles()
    profiles = [p for p in profiles if p['id'] != profile_id]
    save_profiles(profiles)
    return jsonify({"success": True})

@app.route('/api/profiles/<int:profile_id>', methods=['PUT'])
def update_profile(profile_id):
    """Update a profile"""
    data = request.json
    profiles = load_profiles()
    
    for p in profiles:
        if p['id'] == profile_id:
            p['name'] = data.get('name', p['name'])
            p['path'] = data.get('path', p['path'])
            break
    
    save_profiles(profiles)
    return jsonify({"success": True})

@app.route('/api/run', methods=['POST'])
def run_bot():
    """Start the bot on selected profiles"""
    global bot_status
    
    if bot_status["running"]:
        return jsonify({"error": "Bot is already running"}), 400
    
    data = request.json
    selected_profiles = data.get('profiles', [])
    loops = data.get('loops', 1)  # Get loops parameter, default to 1
    
    # Validate loops
    if not isinstance(loops, int) or loops < 1:
        loops = 1
    if loops > 100:  # Set a reasonable maximum
        loops = 100
    
    if not selected_profiles:
        return jsonify({"error": "No profiles selected"}), 400
    
    # Reset completed/failed status before starting new run
    bot_status["completed"] = []
    bot_status["failed"] = []
    bot_status["logs"] = []
    bot_status["task_results"] = {}
    bot_status["queue"] = []
    
    # Run in background thread with loops parameter
    thread = threading.Thread(target=run_bot_sequential, args=(selected_profiles, loops))
    thread.daemon = True
    thread.start()
    
    total_tasks = len(selected_profiles) * loops
    return jsonify({
        "success": True, 
        "message": f"Started queue: {len(selected_profiles)} profiles x {loops} rounds = {total_tasks} tasks"
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current bot status"""
    return jsonify(bot_status)

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the bot (sets flag - actual stop happens after current task)"""
    global bot_status
    bot_status["stop_requested"] = True
    add_log("STOP REQUESTED - Will stop after current task completes", "WARNING")
    return jsonify({"success": True})

@app.route('/api/reset', methods=['POST'])
def reset_status():
    """Reset the bot status"""
    global bot_status
    if bot_status["running"]:
        return jsonify({"error": "Cannot reset while bot is running"}), 400
    
    bot_status = {
        "running": False,
        "stop_requested": False,
        "current_profile": None,
        "current_task": None,
        "current_round": 0,
        "total_rounds": 1,
        "queue": [],
        "current_queue_index": -1,
        "completed": [],
        "failed": [],
        "logs": [],
        "task_results": {}
    }
    return jsonify({"success": True})

# FIX: New endpoint to clear logs from server
@app.route('/api/clear-logs', methods=['POST'])
def clear_logs():
    """Clear the logs array on server side"""
    global bot_status
    bot_status["logs"] = []
    return jsonify({"success": True})

if __name__ == '__main__':
    # Create templates folder if not exists
    os.makedirs('templates', exist_ok=True)
    
    # Create required directories
    os.makedirs('warmupss', exist_ok=True)
    os.makedirs('temp_images', exist_ok=True)
    
    print("\n" + "="*60)
    print("Facebook Warmup Bot - Web Interface".center(60))
    print("="*60)
    print("\n  Dashboard: Open http://localhost:5000 in Chrome")
    print("  Automation: Uses Edge browser profiles")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, port=5000, threaded=True)