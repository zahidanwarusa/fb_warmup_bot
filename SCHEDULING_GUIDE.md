# Facebook Warmup Bot - Scheduling Guide

## Overview

The Facebook Warmup Bot now includes a powerful scheduling system that allows you to automatically run bot sessions at specified times. This eliminates the need to manually start the bot and ensures your Facebook profiles are warmed up consistently.

## Features

- **Multiple Schedule Types**: Once, Daily, Weekly, and Interval-based scheduling
- **Profile Selection**: Choose which profiles to run in each schedule
- **Loop Support**: Configure multiple rounds per schedule
- **Delay Between Rounds**: Set delays between loops (in minutes or hours)
- **Enable/Disable Schedules**: Temporarily disable schedules without deleting them
- **Run Now**: Manually trigger any schedule immediately
- **Automatic Execution**: Schedules run automatically in the background

## Schedule Types

### 1. Once (One-time Schedule)
Runs the bot **one time** at a specific time.

**Example**: Run tomorrow at 9:00 AM
- Schedule Type: `Once`
- Time: `09:00`
- After execution, the schedule is automatically disabled

### 2. Daily
Runs the bot **every day** at a specific time.

**Example**: Run every day at 10:30 AM
- Schedule Type: `Daily`
- Time: `10:30`
- Repeats every 24 hours

### 3. Weekly
Runs the bot on **specific days of the week** at a specific time.

**Example**: Run every Monday, Wednesday, and Friday at 2:00 PM
- Schedule Type: `Weekly`
- Days: `Monday`, `Wednesday`, `Friday`
- Time: `14:00`
- Only runs on the selected days

### 4. Interval
Runs the bot **repeatedly** at a fixed interval.

**Example**: Run every 3 hours
- Schedule Type: `Interval`
- Interval: `3` hours
- Continuous execution with the specified interval between runs

## Using the Scheduler via API

### 1. Create a Schedule

**Endpoint**: `POST /api/schedules`

**Request Body**:
```json
{
  "name": "Daily Morning Warmup",
  "profiles": ["Profile 1", "Profile 2"],
  "loops": 1,
  "loop_delay_value": 0,
  "loop_delay_unit": "minutes",
  "schedule_type": "daily",
  "schedule_time": "09:00",
  "enabled": true
}
```

**Parameters**:
- `name` (required): Name of the schedule
- `profiles` (required): Array of profile names to run
- `loops`: Number of rounds to run (default: 1)
- `loop_delay_value`: Delay between rounds (default: 0)
- `loop_delay_unit`: "minutes" or "hours"
- `schedule_type`: "once", "daily", "weekly", or "interval"
- `schedule_time`: Time in HH:MM format (for once/daily/weekly)
- `schedule_days`: Array of weekday numbers 0-6 for weekly (0=Monday, 6=Sunday)
- `interval_value`: Interval duration (for interval type)
- `interval_unit`: "minutes" or "hours" (for interval type)
- `enabled`: true or false

### 2. Get All Schedules

**Endpoint**: `GET /api/schedules`

**Response**:
```json
[
  {
    "id": 1,
    "name": "Daily Morning Warmup",
    "profiles": ["Profile 1", "Profile 2"],
    "loops": 1,
    "schedule_type": "daily",
    "schedule_time": "09:00",
    "enabled": true,
    "next_run": "2025-12-26T09:00:00",
    "last_run": "2025-12-25T09:00:00",
    "run_count": 5
  }
]
```

### 3. Get Specific Schedule

**Endpoint**: `GET /api/schedules/{schedule_id}`

### 4. Update Schedule

**Endpoint**: `PUT /api/schedules/{schedule_id}`

**Request Body**: Same as create schedule

### 5. Delete Schedule

**Endpoint**: `DELETE /api/schedules/{schedule_id}`

### 6. Enable/Disable Schedule

**Endpoint**: `POST /api/schedules/{schedule_id}/toggle`

**Request Body**:
```json
{
  "enabled": true
}
```

### 7. Run Schedule Immediately

**Endpoint**: `POST /api/schedules/{schedule_id}/run-now`

Triggers the schedule to run immediately without waiting for the scheduled time.

## Example Schedule Configurations

### Example 1: Daily Morning Warmup
```json
{
  "name": "Morning Warmup - All Profiles",
  "profiles": ["Profile 1", "Profile 2", "Profile 3"],
  "loops": 1,
  "loop_delay_value": 0,
  "loop_delay_unit": "minutes",
  "schedule_type": "daily",
  "schedule_time": "08:00",
  "enabled": true
}
```
Runs all 3 profiles once every morning at 8:00 AM.

### Example 2: Weekly Deep Warmup
```json
{
  "name": "Weekly Deep Warmup",
  "profiles": ["Profile 1"],
  "loops": 3,
  "loop_delay_value": 2,
  "loop_delay_unit": "hours",
  "schedule_type": "weekly",
  "schedule_time": "10:00",
  "schedule_days": [0, 2, 4],
  "enabled": true
}
```
Runs Profile 1 on Monday, Wednesday, Friday at 10:00 AM with 3 loops, 2 hours apart.

### Example 3: Continuous Interval Warmup
```json
{
  "name": "Every 4 Hours",
  "profiles": ["Profile 2"],
  "loops": 1,
  "loop_delay_value": 0,
  "loop_delay_unit": "minutes",
  "schedule_type": "interval",
  "interval_value": 4,
  "interval_unit": "hours",
  "enabled": true
}
```
Runs Profile 2 every 4 hours continuously.

### Example 4: One-time Test Run
```json
{
  "name": "Test Run Tomorrow",
  "profiles": ["Profile 3"],
  "loops": 1,
  "loop_delay_value": 0,
  "loop_delay_unit": "minutes",
  "schedule_type": "once",
  "schedule_time": "15:30",
  "enabled": true
}
```
Runs Profile 3 once at 3:30 PM (today or tomorrow if time has passed).

## How It Works

1. **Scheduler Initialization**: When the Flask app starts, the scheduler is initialized and starts running in a background thread.

2. **Next Run Calculation**: For each enabled schedule, the scheduler calculates the next run time based on the schedule type:
   - **Once**: Scheduled time today (or tomorrow if time has passed)
   - **Daily**: Same time every day
   - **Weekly**: Same time on specified weekdays
   - **Interval**: Current time + interval duration

3. **Background Monitoring**: The scheduler checks every 30 seconds if any schedule is due to run.

4. **Execution**: When a schedule's time arrives:
   - The bot runs with the configured profiles, loops, and delays
   - The schedule's `last_run` and `run_count` are updated
   - For recurring schedules, the next run time is calculated
   - For one-time schedules, the schedule is automatically disabled

5. **Persistence**: All schedules are saved to `schedules.json` and persist across app restarts.

## Testing the Scheduler

### Using Python Requests
```python
import requests

# Create a schedule
response = requests.post('http://localhost:5000/api/schedules', json={
    "name": "Test Schedule",
    "profiles": ["Profile 1"],
    "loops": 1,
    "schedule_type": "interval",
    "interval_value": 5,
    "interval_unit": "minutes",
    "enabled": True
})

schedule = response.json()
print(f"Created schedule ID: {schedule['id']}")

# Check all schedules
response = requests.get('http://localhost:5000/api/schedules')
print(response.json())

# Run schedule immediately
requests.post(f'http://localhost:5000/api/schedules/{schedule["id"]}/run-now')

# Disable schedule
requests.post(f'http://localhost:5000/api/schedules/{schedule["id"]}/toggle',
              json={"enabled": False})
```

### Using cURL
```bash
# Create a daily schedule
curl -X POST http://localhost:5000/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Test",
    "profiles": ["Profile 1"],
    "loops": 1,
    "schedule_type": "daily",
    "schedule_time": "12:00",
    "enabled": true
  }'

# Get all schedules
curl http://localhost:5000/api/schedules

# Run schedule 1 now
curl -X POST http://localhost:5000/api/schedules/1/run-now

# Delete schedule 1
curl -X DELETE http://localhost:5000/api/schedules/1
```

## Important Notes

1. **Time Format**: Always use 24-hour format (HH:MM) for schedule times
   - ✅ Correct: "09:00", "14:30", "23:45"
   - ❌ Incorrect: "9:00 AM", "2:30 PM"

2. **Weekday Numbers**: For weekly schedules
   - 0 = Monday
   - 1 = Tuesday
   - 2 = Wednesday
   - 3 = Thursday
   - 4 = Friday
   - 5 = Saturday
   - 6 = Sunday

3. **Bot Running Status**: If the bot is already running (from a manual start or another schedule), new schedules will wait until it finishes.

4. **One-time Schedules**: Automatically disabled after execution. Re-enable and update the time to run again.

5. **Scheduler Checks**: The scheduler checks for due schedules every 30 seconds, so execution may be up to 30 seconds after the scheduled time.

6. **File Persistence**: Schedules are stored in `schedules.json` in the app directory.

## Monitoring Schedules

Check the status endpoint to see if a scheduled run is active:

```bash
curl http://localhost:5000/api/status
```

The response includes `schedule_id` if the current run was triggered by a schedule.

## Troubleshooting

### Schedule Not Running
1. Check if schedule is enabled: `GET /api/schedules/{id}`
2. Verify `next_run` time is in the future
3. Check app logs for scheduler errors
4. Ensure profiles exist in the profiles list

### Unexpected Timing
1. Verify time format is HH:MM in 24-hour format
2. For weekly schedules, check weekday numbers (0-6)
3. Check system time on the server

### Schedule Conflicts
If multiple schedules are set to run at the same time, they will run sequentially in the order they were created.

## Best Practices

1. **Start Small**: Begin with interval or once schedules to test
2. **Avoid Overlaps**: Space schedules apart to avoid queuing
3. **Use Descriptive Names**: Clearly identify what each schedule does
4. **Monitor Initial Runs**: Check logs after creating new schedules
5. **Regular Maintenance**: Review and clean up old schedules periodically

## Advanced Usage

### Staggered Profile Warmup
Create separate schedules for different profiles at different times to simulate natural activity patterns:

```python
# Morning batch
POST /api/schedules
{
  "name": "Morning Batch A",
  "profiles": ["Profile 1", "Profile 2"],
  "schedule_type": "daily",
  "schedule_time": "08:00"
}

# Afternoon batch
POST /api/schedules
{
  "name": "Afternoon Batch B",
  "profiles": ["Profile 3", "Profile 4"],
  "schedule_type": "daily",
  "schedule_time": "14:00"
}
```

### Weekend vs Weekday Patterns
```python
# Weekday schedule
{
  "schedule_type": "weekly",
  "schedule_days": [0, 1, 2, 3, 4],  # Mon-Fri
  "schedule_time": "09:00"
}

# Weekend schedule
{
  "schedule_type": "weekly",
  "schedule_days": [5, 6],  # Sat-Sun
  "schedule_time": "11:00"
}
```

## Support

For issues or questions about the scheduler:
1. Check the app logs for error messages
2. Verify schedule configuration via GET endpoints
3. Test with a simple once or interval schedule first
4. Review this guide for correct parameter formats
