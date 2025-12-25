# Facebook Warmup Bot - Scheduling Feature

## New Feature: Automatic Scheduling

Your Facebook Warmup Bot now includes a powerful scheduling system that allows you to automatically run warmup sessions at specified times without manual intervention.

## Quick Start

### 1. Start the application
```bash
python app.py
```

You should see:
```
[SCHEDULER] Scheduler started
```

### 2. Create your first schedule

**Option A: Using cURL**
```bash
curl -X POST http://localhost:5000/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Morning Warmup",
    "profiles": ["Profile 1"],
    "loops": 1,
    "schedule_type": "daily",
    "schedule_time": "09:00",
    "enabled": true
  }'
```

**Option B: Using Python**
```python
import requests

requests.post('http://localhost:5000/api/schedules', json={
    "name": "Daily Morning Warmup",
    "profiles": ["Profile 1"],
    "loops": 1,
    "schedule_type": "daily",
    "schedule_time": "09:00",
    "enabled": True
})
```

**Option C: Using the helper script**
```bash
python schedule_manager.py
```
Then edit the file and uncomment the examples.

### 3. Verify your schedule
```bash
curl http://localhost:5000/api/schedules
```

That's it! Your bot will now run automatically at the scheduled time.

## What Can You Schedule?

### 1. **Daily** - Run every day at a specific time
```json
{
  "schedule_type": "daily",
  "schedule_time": "09:00"
}
```

### 2. **Weekly** - Run on specific days of the week
```json
{
  "schedule_type": "weekly",
  "schedule_time": "10:00",
  "schedule_days": [0, 1, 2, 3, 4]  // Monday-Friday
}
```

### 3. **Interval** - Run repeatedly at fixed intervals
```json
{
  "schedule_type": "interval",
  "interval_value": 3,
  "interval_unit": "hours"
}
```

### 4. **Once** - Run one time (for testing)
```json
{
  "schedule_type": "once",
  "schedule_time": "15:30"
}
```

## Common Use Cases

### Use Case 1: Business Hours Only
Run 3 times a day during business hours (Mon-Fri):

```bash
# Morning - 9 AM
curl -X POST http://localhost:5000/api/schedules -H "Content-Type: application/json" -d '{
  "name": "Morning", "profiles": ["Profile 1"], "schedule_type": "weekly",
  "schedule_time": "09:00", "schedule_days": [0,1,2,3,4], "enabled": true
}'

# Lunch - 1 PM
curl -X POST http://localhost:5000/api/schedules -H "Content-Type: application/json" -d '{
  "name": "Lunch", "profiles": ["Profile 1"], "schedule_type": "weekly",
  "schedule_time": "13:00", "schedule_days": [0,1,2,3,4], "enabled": true
}'

# Evening - 5 PM
curl -X POST http://localhost:5000/api/schedules -H "Content-Type: application/json" -d '{
  "name": "Evening", "profiles": ["Profile 1"], "schedule_type": "weekly",
  "schedule_time": "17:00", "schedule_days": [0,1,2,3,4], "enabled": true
}'
```

### Use Case 2: Round-the-Clock
Run every 4 hours continuously:

```bash
curl -X POST http://localhost:5000/api/schedules -H "Content-Type: application/json" -d '{
  "name": "Every 4 Hours",
  "profiles": ["Profile 1", "Profile 2"],
  "schedule_type": "interval",
  "interval_value": 4,
  "interval_unit": "hours",
  "enabled": true
}'
```

### Use Case 3: Different Profiles at Different Times
Stagger your profiles throughout the day:

```python
import requests

base_url = 'http://localhost:5000/api/schedules'

# Profile 1 at 8 AM
requests.post(base_url, json={
    "name": "Profile 1 - Morning",
    "profiles": ["Profile 1"],
    "schedule_type": "daily",
    "schedule_time": "08:00",
    "enabled": True
})

# Profile 2 at 12 PM
requests.post(base_url, json={
    "name": "Profile 2 - Noon",
    "profiles": ["Profile 2"],
    "schedule_type": "daily",
    "schedule_time": "12:00",
    "enabled": True
})

# Profile 3 at 6 PM
requests.post(base_url, json={
    "name": "Profile 3 - Evening",
    "profiles": ["Profile 3"],
    "schedule_type": "daily",
    "schedule_time": "18:00",
    "enabled": True
})
```

## Managing Schedules

### List all schedules
```bash
curl http://localhost:5000/api/schedules
```

### Get specific schedule
```bash
curl http://localhost:5000/api/schedules/1
```

### Disable a schedule (without deleting)
```bash
curl -X POST http://localhost:5000/api/schedules/1/toggle \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### Run a schedule immediately
```bash
curl -X POST http://localhost:5000/api/schedules/1/run-now
```

### Delete a schedule
```bash
curl -X DELETE http://localhost:5000/api/schedules/1
```

## Testing the Scheduler

Run the automated test suite to verify everything works:

```bash
python test_scheduler.py
```

This will run 8 tests and show you the results.

## Files and Documentation

- **SCHEDULING_GUIDE.md** - Complete documentation with all details
- **QUICK_START_SCHEDULING.md** - Quick reference with examples
- **SCHEDULING_SUMMARY.md** - Implementation summary
- **schedule_manager.py** - Helper script for managing schedules
- **test_scheduler.py** - Automated test suite

## How It Works

1. The scheduler runs in a background thread
2. Checks every 30 seconds for schedules that are due
3. When a schedule is due, it triggers the bot automatically
4. For recurring schedules, it calculates the next run time
5. All schedules are saved to `schedules.json` and persist across restarts

## Important Notes

- ✅ Time format must be 24-hour (HH:MM): "09:00" not "9:00 AM"
- ✅ Weekdays are numbered 0-6 (0=Monday, 6=Sunday)
- ✅ Schedules persist across app restarts
- ✅ One-time schedules auto-disable after running
- ✅ If bot is running, new schedules wait until it finishes

## Troubleshooting

**Schedule not running?**
- Verify it's enabled: `curl http://localhost:5000/api/schedules/1`
- Check `next_run` is in the future
- Ensure profile names match exactly

**Wrong time?**
- Use 24-hour format: "14:00" not "2:00 PM"
- Check your system time is correct

**Need help?**
- See SCHEDULING_GUIDE.md for detailed documentation
- Run test_scheduler.py to diagnose issues

## Examples Repository

All examples are in the documentation files:
- Simple examples: QUICK_START_SCHEDULING.md
- Advanced examples: SCHEDULING_GUIDE.md
- Python script: schedule_manager.py

## Getting Started Checklist

- [ ] Start the app: `python app.py`
- [ ] Verify scheduler is running (check console output)
- [ ] Create a test schedule with interval type (5 minutes)
- [ ] Verify schedule: `curl http://localhost:5000/api/schedules`
- [ ] Trigger it manually: `curl -X POST http://localhost:5000/api/schedules/1/run-now`
- [ ] Watch it run in the dashboard
- [ ] Create your daily schedules
- [ ] Monitor for 24 hours to ensure it works

## Support

If you need help:
1. Read SCHEDULING_GUIDE.md
2. Run test_scheduler.py
3. Check the app console for errors
4. Verify your schedule configuration

Enjoy automatic warmups!
