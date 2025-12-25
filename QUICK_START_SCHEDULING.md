# Quick Start: Scheduling Your Facebook Warmup Bot

## Simple Examples to Get Started

### Example 1: Run Every Day at 9 AM

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

### Example 2: Run Every 2 Hours

```bash
curl -X POST http://localhost:5000/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Every 2 Hours",
    "profiles": ["Profile 1"],
    "loops": 1,
    "schedule_type": "interval",
    "interval_value": 2,
    "interval_unit": "hours",
    "enabled": true
  }'
```

### Example 3: Run Monday-Friday at 10:30 AM

```bash
curl -X POST http://localhost:5000/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekday Warmup",
    "profiles": ["Profile 1", "Profile 2"],
    "loops": 1,
    "schedule_type": "weekly",
    "schedule_time": "10:30",
    "schedule_days": [0, 1, 2, 3, 4],
    "enabled": true
  }'
```

### Example 4: One-Time Run Tomorrow at 3 PM

```bash
curl -X POST http://localhost:5000/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "One Time Test",
    "profiles": ["Profile 1"],
    "loops": 1,
    "schedule_type": "once",
    "schedule_time": "15:00",
    "enabled": true
  }'
```

## Python Examples

### Create a Daily Schedule

```python
import requests

response = requests.post('http://localhost:5000/api/schedules', json={
    "name": "Daily Warmup",
    "profiles": ["Profile 1"],
    "loops": 1,
    "schedule_type": "daily",
    "schedule_time": "08:00",
    "enabled": True
})

print(f"Created schedule: {response.json()}")
```

### View All Schedules

```python
import requests

response = requests.get('http://localhost:5000/api/schedules')
schedules = response.json()

for schedule in schedules:
    print(f"ID: {schedule['id']}")
    print(f"Name: {schedule['name']}")
    print(f"Type: {schedule['schedule_type']}")
    print(f"Next Run: {schedule.get('next_run', 'N/A')}")
    print(f"Enabled: {schedule['enabled']}")
    print("-" * 40)
```

### Disable a Schedule

```python
import requests

schedule_id = 1
response = requests.post(
    f'http://localhost:5000/api/schedules/{schedule_id}/toggle',
    json={"enabled": False}
)

print(f"Schedule disabled: {response.json()}")
```

### Delete a Schedule

```python
import requests

schedule_id = 1
response = requests.delete(f'http://localhost:5000/api/schedules/{schedule_id}')

print(f"Schedule deleted: {response.json()}")
```

### Run a Schedule Immediately

```python
import requests

schedule_id = 1
response = requests.post(f'http://localhost:5000/api/schedules/{schedule_id}/run-now')

print(f"Schedule triggered: {response.json()}")
```

## Understanding Schedule Types

### 1. **Daily** - Same time every day
- Best for: Consistent daily warmup routine
- `schedule_type`: "daily"
- `schedule_time`: "HH:MM" (24-hour format)

### 2. **Weekly** - Specific days of the week
- Best for: Different patterns on different days
- `schedule_type`: "weekly"
- `schedule_time`: "HH:MM"
- `schedule_days`: [0, 1, 2, 3, 4, 5, 6] (0=Mon, 6=Sun)

### 3. **Interval** - Regular intervals
- Best for: Continuous activity throughout the day
- `schedule_type`: "interval"
- `interval_value`: Number (e.g., 2, 4, 6)
- `interval_unit`: "minutes" or "hours"

### 4. **Once** - One-time run
- Best for: Testing or special one-off runs
- `schedule_type`: "once"
- `schedule_time`: "HH:MM"
- Note: Automatically disables after running

## Common Patterns

### Pattern 1: Business Hours Only (9 AM - 5 PM, Mon-Fri)

Create 3 schedules:
```python
import requests

base_url = 'http://localhost:5000/api/schedules'

# Morning (9 AM)
requests.post(base_url, json={
    "name": "Morning - Weekdays",
    "profiles": ["Profile 1"],
    "schedule_type": "weekly",
    "schedule_time": "09:00",
    "schedule_days": [0, 1, 2, 3, 4],
    "enabled": True
})

# Lunch (1 PM)
requests.post(base_url, json={
    "name": "Afternoon - Weekdays",
    "profiles": ["Profile 1"],
    "schedule_type": "weekly",
    "schedule_time": "13:00",
    "schedule_days": [0, 1, 2, 3, 4],
    "enabled": True
})

# Evening (5 PM)
requests.post(base_url, json={
    "name": "Evening - Weekdays",
    "profiles": ["Profile 1"],
    "schedule_type": "weekly",
    "schedule_time": "17:00",
    "schedule_days": [0, 1, 2, 3, 4],
    "enabled": True
})
```

### Pattern 2: Round-the-Clock Every 4 Hours

```python
import requests

requests.post('http://localhost:5000/api/schedules', json={
    "name": "24/7 Every 4 Hours",
    "profiles": ["Profile 1", "Profile 2"],
    "schedule_type": "interval",
    "interval_value": 4,
    "interval_unit": "hours",
    "enabled": True
})
```

### Pattern 3: Different Profiles at Different Times

```python
import requests

base_url = 'http://localhost:5000/api/schedules'

# Profile 1 at 8 AM
requests.post(base_url, json={
    "name": "Profile 1 Morning",
    "profiles": ["Profile 1"],
    "schedule_type": "daily",
    "schedule_time": "08:00",
    "enabled": True
})

# Profile 2 at 12 PM
requests.post(base_url, json={
    "name": "Profile 2 Noon",
    "profiles": ["Profile 2"],
    "schedule_type": "daily",
    "schedule_time": "12:00",
    "enabled": True
})

# Profile 3 at 6 PM
requests.post(base_url, json={
    "name": "Profile 3 Evening",
    "profiles": ["Profile 3"],
    "schedule_type": "daily",
    "schedule_time": "18:00",
    "enabled": True
})
```

## Tips

1. **Start Simple**: Begin with a single daily schedule to test
2. **Check Next Run**: After creating, verify the `next_run` time is correct
3. **Monitor First Run**: Watch the logs during the first scheduled execution
4. **Use Descriptive Names**: Make it easy to identify schedules later
5. **Test with "Run Now"**: Use the run-now endpoint to test before waiting for scheduled time

## Checking Status

```bash
# Get all schedules
curl http://localhost:5000/api/schedules

# Get bot status (see if running from schedule)
curl http://localhost:5000/api/status
```

## Need More Help?

See the full [SCHEDULING_GUIDE.md](SCHEDULING_GUIDE.md) for detailed documentation.
