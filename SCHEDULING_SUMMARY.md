# Scheduling Feature - Implementation Summary

## What Was Added

The Facebook Warmup Bot now includes a complete scheduling system that allows automatic execution of bot sessions at specified times.

## Files Added

1. **scheduler.py** - Core scheduling engine
   - BotScheduler class that manages all schedules
   - Support for 4 schedule types: Once, Daily, Weekly, Interval
   - Background thread that checks and executes schedules
   - Persistent storage in schedules.json

2. **SCHEDULING_GUIDE.md** - Complete documentation
   - Detailed explanation of all schedule types
   - API endpoint reference
   - Example configurations
   - Troubleshooting guide

3. **QUICK_START_SCHEDULING.md** - Quick reference
   - Simple copy-paste examples
   - Common usage patterns
   - Python and cURL examples

4. **schedule_manager.py** - Helper utility
   - Python script for easy schedule management
   - Functions to create, list, delete schedules
   - Command-line interface

## Files Modified

**app.py** - Flask application
- Imported BotScheduler
- Added scheduler initialization on startup
- Added 7 new API endpoints for schedule management
- Modified run_bot_sequential to accept schedule_id parameter
- Added schedule_id to bot_status tracking

## New API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/schedules | Get all schedules |
| POST | /api/schedules | Create a new schedule |
| GET | /api/schedules/{id} | Get specific schedule |
| PUT | /api/schedules/{id} | Update schedule |
| DELETE | /api/schedules/{id} | Delete schedule |
| POST | /api/schedules/{id}/toggle | Enable/disable schedule |
| POST | /api/schedules/{id}/run-now | Run schedule immediately |

## Schedule Types

### 1. Once
Run one time at a specific time. Automatically disables after execution.

**Use case**: Test runs, special one-off warmups

**Example**:
```json
{
  "schedule_type": "once",
  "schedule_time": "15:30"
}
```

### 2. Daily
Run every day at the same time.

**Use case**: Regular daily warmup routine

**Example**:
```json
{
  "schedule_type": "daily",
  "schedule_time": "09:00"
}
```

### 3. Weekly
Run on specific days of the week at a specific time.

**Use case**: Different patterns for weekdays vs weekends

**Example**:
```json
{
  "schedule_type": "weekly",
  "schedule_time": "10:00",
  "schedule_days": [0, 1, 2, 3, 4]
}
```

### 4. Interval
Run repeatedly at fixed intervals.

**Use case**: Continuous activity throughout the day

**Example**:
```json
{
  "schedule_type": "interval",
  "interval_value": 3,
  "interval_unit": "hours"
}
```

## How It Works

1. **Initialization**: Scheduler starts when Flask app starts
2. **Background Thread**: Checks every 30 seconds for due schedules
3. **Execution**: When a schedule is due, it triggers run_bot_sequential
4. **Next Run Calculation**: Automatically calculates next run time for recurring schedules
5. **Persistence**: All schedules saved to schedules.json

## Key Features

- ✅ Multiple schedule types (once, daily, weekly, interval)
- ✅ Support for multiple profiles per schedule
- ✅ Loop support with configurable delays
- ✅ Enable/disable schedules without deleting
- ✅ Manual trigger (run now) functionality
- ✅ Persistent storage across restarts
- ✅ Automatic next-run calculation
- ✅ Run count and last-run tracking
- ✅ Non-blocking background execution
- ✅ Integration with existing bot status system

## Quick Test

### 1. Start the app
```bash
python app.py
```

You should see:
```
[SCHEDULER] Started
```

### 2. Create a test schedule (runs every 5 minutes)
```bash
curl -X POST http://localhost:5000/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Schedule",
    "profiles": ["Profile 1"],
    "loops": 1,
    "schedule_type": "interval",
    "interval_value": 5,
    "interval_unit": "minutes",
    "enabled": true
  }'
```

### 3. Verify schedule was created
```bash
curl http://localhost:5000/api/schedules
```

### 4. Trigger immediately (don't wait 5 minutes)
```bash
curl -X POST http://localhost:5000/api/schedules/1/run-now
```

### 5. Check bot status
```bash
curl http://localhost:5000/api/status
```

## Using Python

```python
import requests

# Create schedule
response = requests.post('http://localhost:5000/api/schedules', json={
    "name": "Daily Morning",
    "profiles": ["Profile 1"],
    "loops": 1,
    "schedule_type": "daily",
    "schedule_time": "08:00",
    "enabled": True
})
print(response.json())

# List schedules
response = requests.get('http://localhost:5000/api/schedules')
for schedule in response.json():
    print(f"{schedule['id']}: {schedule['name']} - {schedule['schedule_type']}")
```

## Using the Helper Script

```bash
python schedule_manager.py
```

This will list all schedules and show bot status. Edit the file to uncomment example code for creating schedules.

## Configuration Examples

### Basic Daily Warmup
```json
{
  "name": "Daily 9 AM",
  "profiles": ["Profile 1"],
  "loops": 1,
  "schedule_type": "daily",
  "schedule_time": "09:00",
  "enabled": true
}
```

### Weekday Only
```json
{
  "name": "Weekdays 10 AM",
  "profiles": ["Profile 1", "Profile 2"],
  "loops": 1,
  "schedule_type": "weekly",
  "schedule_time": "10:00",
  "schedule_days": [0, 1, 2, 3, 4],
  "enabled": true
}
```

### Every 4 Hours
```json
{
  "name": "Every 4 Hours",
  "profiles": ["Profile 1"],
  "loops": 1,
  "schedule_type": "interval",
  "interval_value": 4,
  "interval_unit": "hours",
  "enabled": true
}
```

### Multiple Rounds with Delay
```json
{
  "name": "3 Rounds Daily",
  "profiles": ["Profile 1"],
  "loops": 3,
  "loop_delay_value": 2,
  "loop_delay_unit": "hours",
  "schedule_type": "daily",
  "schedule_time": "08:00",
  "enabled": true
}
```

## Monitoring

### Check All Schedules
```bash
curl http://localhost:5000/api/schedules
```

### Check Bot Status
```bash
curl http://localhost:5000/api/status
```

If a schedule triggered the current run, you'll see:
```json
{
  "running": true,
  "schedule_id": 1,
  "current_profile": "Profile 1",
  ...
}
```

## Troubleshooting

### Schedule not running?
1. Check if enabled: `GET /api/schedules/{id}`
2. Verify next_run is in the future
3. Check app console for errors
4. Ensure profiles exist

### Wrong timing?
1. Verify 24-hour time format (09:00, not 9:00 AM)
2. Check weekday numbers for weekly (0=Monday)
3. Verify server system time

### Multiple schedules at same time?
They run sequentially in creation order. Space them out to avoid queuing.

## Important Notes

- ✅ Scheduler runs automatically when app starts
- ✅ Schedules persist across restarts (saved to schedules.json)
- ✅ One-time schedules auto-disable after running
- ✅ Scheduler checks every 30 seconds (execution may be up to 30s after scheduled time)
- ✅ If bot is running, new schedules wait until it finishes
- ✅ Time format must be HH:MM in 24-hour format
- ✅ Weekday numbers: 0=Monday, 6=Sunday

## Next Steps

1. **Test with a simple schedule**: Create an interval schedule for 5 minutes and verify it works
2. **Set up your daily routine**: Create daily schedules for your regular warmup times
3. **Monitor the first few runs**: Check logs to ensure everything works as expected
4. **Adjust as needed**: Modify intervals and times based on your needs

## Documentation

- **Full Guide**: See [SCHEDULING_GUIDE.md](SCHEDULING_GUIDE.md)
- **Quick Reference**: See [QUICK_START_SCHEDULING.md](QUICK_START_SCHEDULING.md)
- **Helper Tool**: Use [schedule_manager.py](schedule_manager.py)

## Support

If you encounter issues:
1. Check the console output for scheduler logs
2. Verify schedule configuration via GET endpoint
3. Test with "run-now" before relying on scheduled time
4. Review the documentation for correct parameter formats
