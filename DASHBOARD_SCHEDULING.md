# Dashboard Scheduling Feature - Complete!

## What's New

Your Facebook Warmup Bot dashboard now has a **Schedules** tab with a full UI for creating and managing automated schedules!

## How to Use

### 1. Start the Application
```bash
python app.py
```

### 2. Open the Dashboard
Navigate to: `http://localhost:5000`

### 3. You'll See Two Tabs:
- **Manual Run** - Your existing interface for running the bot manually
- **Schedules** - NEW! Create and manage automated schedules

## Creating a Schedule via Dashboard

### Step 1: Click the "Schedules" Tab

### Step 2: Fill Out the Schedule Form

**Schedule Name**: Give it a descriptive name (e.g., "Daily Morning Warmup")

**Select Profiles**: Check the profiles you want to include

**Schedule Type**: Choose from 4 options:
- **Daily**: Runs every day at a specific time
- **Weekly**: Runs on specific days of the week
- **Interval**: Runs repeatedly at fixed intervals
- **Once**: Runs one time only

**Time**: Set the time (for Daily, Weekly, Once types)

**Days of Week**: Select days (for Weekly type only)

**Interval**: Set interval duration (for Interval type only)

**Warmup Rounds**: Number of loops to run

**Loop Delay**: Delay between rounds

### Step 3: Click "Create Schedule"

Your schedule is now active and will run automatically!

## Managing Schedules

### View All Schedules
All your schedules appear in the right panel with:
- Name and details
- Next run time
- Number of times it has run
- Enable/disable toggle
- Action buttons

### Enable/Disable a Schedule
Click the toggle switch to enable (green) or disable (gray)

### Run a Schedule Immediately
Click "Run Now" to trigger the schedule without waiting

### Delete a Schedule
Click "Delete" and confirm

## Schedule Examples

### Example 1: Daily at 9 AM
1. Click "Schedules" tab
2. Enter name: "Daily Morning"
3. Select profiles
4. Schedule Type: Daily
5. Time: 09:00
6. Rounds: 1
7. Click "Create Schedule"

### Example 2: Every 4 Hours
1. Click "Schedules" tab
2. Enter name: "Every 4 Hours"
3. Select profiles
4. Schedule Type: Interval
5. Interval: 4 hours
6. Rounds: 1
7. Click "Create Schedule"

### Example 3: Weekdays at 10 AM
1. Click "Schedules" tab
2. Enter name: "Weekday Warmup"
3. Select profiles
4. Schedule Type: Weekly
5. Time: 10:00
6. Days: Check Mon, Tue, Wed, Thu, Fri
7. Rounds: 1
8. Click "Create Schedule"

## Features

✅ **Visual Schedule Management**: See all schedules at a glance
✅ **Toggle On/Off**: Enable/disable without deleting
✅ **Run Now**: Test schedules immediately
✅ **Next Run Time**: See when each schedule will run next
✅ **Run Counter**: Track how many times each schedule has executed
✅ **Multi-Profile Support**: Run multiple profiles in one schedule
✅ **Flexible Timing**: Daily, weekly, interval, or one-time runs
✅ **Automatic Execution**: Runs in background without manual intervention

## What Happens When a Schedule Runs

1. At the scheduled time, the bot automatically starts
2. You'll see the execution in the "Manual Run" tab status
3. Logs are recorded just like manual runs
4. When complete, the next run time is calculated
5. One-time schedules automatically disable after running

## Tips

💡 **Start Simple**: Create an interval schedule for 5 minutes to test

💡 **Use Descriptive Names**: "Morning Batch" is better than "Schedule 1"

💡 **Check Next Run Time**: Verify the schedule will run when you expect

💡 **Toggle Instead of Delete**: Disable schedules you might want later

💡 **Monitor First Runs**: Watch the first execution to ensure it works

## Dashboard Features

### Schedules Tab (Left Side)
- Create new schedules
- Select profiles from a list
- Choose schedule type and timing
- Set rounds and delays

### Active Schedules (Right Side)
- View all schedules
- See status (enabled/disabled)
- Next run time
- Run count
- Quick actions (toggle, run now, delete)

## Files Created/Modified

**Modified**:
- `templates/index.html` - Added Schedules tab and UI

**Created**:
- `static/app.js` - Frontend JavaScript for scheduling
- `scheduler.py` - Backend scheduler engine (already created)

## Backend API

The dashboard uses these API endpoints:
- `GET /api/schedules` - List all schedules
- `POST /api/schedules` - Create schedule
- `DELETE /api/schedules/{id}` - Delete schedule
- `POST /api/schedules/{id}/toggle` - Enable/disable
- `POST /api/schedules/{id}/run-now` - Trigger immediately

## Troubleshooting

### Schedule Not Showing Up?
- Refresh the page
- Check browser console for errors
- Verify Flask app is running

### Can't Create Schedule?
- Ensure you have profiles added
- Check all required fields are filled
- For weekly, select at least one day

### Schedule Not Running?
- Check it's enabled (green toggle)
- Verify next run time is in the future
- Check system time is correct

## Next Steps

1. Open `http://localhost:5000`
2. Click "Schedules" tab
3. Create your first schedule
4. Test it with "Run Now"
5. Let it run automatically!

## Additional Documentation

For more details on scheduling:
- `SCHEDULING_GUIDE.md` - Complete API documentation
- `QUICK_START_SCHEDULING.md` - Command-line examples
- `README_SCHEDULING.md` - Overview and quick start

Enjoy automated warmups! 🎉
