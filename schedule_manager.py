"""
Schedule Manager - Helper script to manage bot schedules
Easy command-line interface for creating and managing schedules
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:5000/api"

def create_daily_schedule(name, profiles, time, loops=1):
    """
    Create a daily schedule

    Args:
        name: Schedule name
        profiles: List of profile names
        time: Time in HH:MM format (24-hour)
        loops: Number of rounds (default: 1)
    """
    data = {
        "name": name,
        "profiles": profiles,
        "loops": loops,
        "schedule_type": "daily",
        "schedule_time": time,
        "enabled": True
    }

    response = requests.post(f"{API_BASE}/schedules", json=data)
    if response.status_code == 200:
        schedule = response.json()
        print(f"✓ Created daily schedule '{name}'")
        print(f"  ID: {schedule['id']}")
        print(f"  Next run: {schedule.get('next_run', 'Calculating...')}")
        return schedule
    else:
        print(f"✗ Error: {response.json()}")
        return None

def create_interval_schedule(name, profiles, interval_value, interval_unit="hours", loops=1):
    """
    Create an interval-based schedule

    Args:
        name: Schedule name
        profiles: List of profile names
        interval_value: Interval duration
        interval_unit: "minutes" or "hours"
        loops: Number of rounds (default: 1)
    """
    data = {
        "name": name,
        "profiles": profiles,
        "loops": loops,
        "schedule_type": "interval",
        "interval_value": interval_value,
        "interval_unit": interval_unit,
        "enabled": True
    }

    response = requests.post(f"{API_BASE}/schedules", json=data)
    if response.status_code == 200:
        schedule = response.json()
        print(f"✓ Created interval schedule '{name}'")
        print(f"  ID: {schedule['id']}")
        print(f"  Interval: Every {interval_value} {interval_unit}")
        print(f"  Next run: {schedule.get('next_run', 'Calculating...')}")
        return schedule
    else:
        print(f"✗ Error: {response.json()}")
        return None

def create_weekly_schedule(name, profiles, time, days, loops=1):
    """
    Create a weekly schedule

    Args:
        name: Schedule name
        profiles: List of profile names
        time: Time in HH:MM format (24-hour)
        days: List of weekday numbers (0=Monday, 6=Sunday)
        loops: Number of rounds (default: 1)
    """
    data = {
        "name": name,
        "profiles": profiles,
        "loops": loops,
        "schedule_type": "weekly",
        "schedule_time": time,
        "schedule_days": days,
        "enabled": True
    }

    response = requests.post(f"{API_BASE}/schedules", json=data)
    if response.status_code == 200:
        schedule = response.json()
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        selected_days = ", ".join([day_names[d] for d in days])
        print(f"✓ Created weekly schedule '{name}'")
        print(f"  ID: {schedule['id']}")
        print(f"  Days: {selected_days}")
        print(f"  Next run: {schedule.get('next_run', 'Calculating...')}")
        return schedule
    else:
        print(f"✗ Error: {response.json()}")
        return None

def list_schedules():
    """List all schedules"""
    response = requests.get(f"{API_BASE}/schedules")
    if response.status_code == 200:
        schedules = response.json()

        if not schedules:
            print("No schedules found")
            return

        print(f"\n{'='*70}")
        print(f"{'SCHEDULES':^70}")
        print(f"{'='*70}")

        for schedule in schedules:
            status = "✓ Enabled" if schedule['enabled'] else "✗ Disabled"

            print(f"\nID: {schedule['id']} | {schedule['name']} | {status}")
            print(f"  Type: {schedule['schedule_type'].upper()}")
            print(f"  Profiles: {', '.join(schedule['profiles'])}")
            print(f"  Loops: {schedule['loops']}")

            if schedule['schedule_type'] in ['daily', 'weekly', 'once']:
                print(f"  Time: {schedule['schedule_time']}")

            if schedule['schedule_type'] == 'weekly':
                day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                days = schedule.get('schedule_days', [])
                selected_days = ", ".join([day_names[d] for d in days])
                print(f"  Days: {selected_days}")

            if schedule['schedule_type'] == 'interval':
                print(f"  Interval: Every {schedule['interval_value']} {schedule['interval_unit']}")

            if schedule.get('next_run'):
                next_run = datetime.fromisoformat(schedule['next_run'])
                print(f"  Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

            if schedule.get('last_run'):
                last_run = datetime.fromisoformat(schedule['last_run'])
                print(f"  Last run: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")

            print(f"  Run count: {schedule.get('run_count', 0)}")

        print(f"\n{'='*70}\n")
    else:
        print(f"✗ Error fetching schedules")

def delete_schedule(schedule_id):
    """Delete a schedule"""
    response = requests.delete(f"{API_BASE}/schedules/{schedule_id}")
    if response.status_code == 200:
        print(f"✓ Deleted schedule ID {schedule_id}")
        return True
    else:
        print(f"✗ Error deleting schedule")
        return False

def toggle_schedule(schedule_id, enabled):
    """Enable or disable a schedule"""
    response = requests.post(
        f"{API_BASE}/schedules/{schedule_id}/toggle",
        json={"enabled": enabled}
    )
    if response.status_code == 200:
        status = "enabled" if enabled else "disabled"
        print(f"✓ Schedule ID {schedule_id} {status}")
        return True
    else:
        print(f"✗ Error toggling schedule")
        return False

def run_schedule_now(schedule_id):
    """Run a schedule immediately"""
    response = requests.post(f"{API_BASE}/schedules/{schedule_id}/run-now")
    if response.status_code == 200:
        print(f"✓ Schedule ID {schedule_id} triggered")
        print(f"  Check http://localhost:5000 for progress")
        return True
    else:
        error = response.json().get('error', 'Unknown error')
        print(f"✗ Error: {error}")
        return False

def get_bot_status():
    """Get current bot status"""
    response = requests.get(f"{API_BASE}/status")
    if response.status_code == 200:
        status = response.json()

        print(f"\n{'='*70}")
        print(f"{'BOT STATUS':^70}")
        print(f"{'='*70}")

        if status['running']:
            print(f"Status: RUNNING")
            if status.get('schedule_id'):
                print(f"Triggered by: Schedule ID {status['schedule_id']}")
            print(f"Current profile: {status.get('current_profile', 'N/A')}")
            print(f"Current task: {status.get('current_task', 'N/A')}")
            print(f"Round: {status.get('current_round', 0)}/{status.get('total_rounds', 0)}")

            if status.get('is_delaying'):
                print(f"Delaying: {status['delay_remaining']} seconds remaining")
        else:
            print(f"Status: IDLE")

        print(f"\n{'='*70}\n")
    else:
        print(f"✗ Error fetching status")

# Example usage
if __name__ == "__main__":
    print("\n" + "="*70)
    print("Facebook Warmup Bot - Schedule Manager".center(70))
    print("="*70 + "\n")

    # Example: Create a daily schedule
    # Uncomment to use:
    # create_daily_schedule(
    #     name="Morning Warmup",
    #     profiles=["Profile 1"],
    #     time="09:00",
    #     loops=1
    # )

    # Example: Create an interval schedule
    # Uncomment to use:
    # create_interval_schedule(
    #     name="Every 3 Hours",
    #     profiles=["Profile 1", "Profile 2"],
    #     interval_value=3,
    #     interval_unit="hours",
    #     loops=1
    # )

    # Example: Create a weekly schedule (Monday-Friday at 10 AM)
    # Uncomment to use:
    # create_weekly_schedule(
    #     name="Weekday Warmup",
    #     profiles=["Profile 1"],
    #     time="10:00",
    #     days=[0, 1, 2, 3, 4],  # Mon-Fri
    #     loops=1
    # )

    # List all schedules
    list_schedules()

    # Get bot status
    get_bot_status()

    print("\nTo create schedules, uncomment the example code in this file")
    print("and modify the parameters as needed.\n")
