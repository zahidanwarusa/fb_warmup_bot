"""
Scheduler Module for Facebook Warmup Bot
Handles time-based scheduling of bot runs
"""

import threading
import time
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

SCHEDULES_FILE = "schedules.json"

class BotScheduler:
    """Manages scheduled bot runs"""

    def __init__(self, run_bot_callback):
        """
        Initialize scheduler

        Args:
            run_bot_callback: Function to call when executing a scheduled task
                             Should accept (selected_profiles, loops, loop_delay_seconds, schedule_id)
        """
        self.run_bot_callback = run_bot_callback
        self.schedules = self.load_schedules()
        self.running = False
        self.scheduler_thread = None
        self.next_run_times = {}  # schedule_id -> next_datetime

    def load_schedules(self):
        """Load schedules from JSON file"""
        if os.path.exists(SCHEDULES_FILE):
            try:
                with open(SCHEDULES_FILE, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_schedules(self):
        """Save schedules to JSON file"""
        with open(SCHEDULES_FILE, 'w') as f:
            json.dump(self.schedules, f, indent=2)

    def add_schedule(self, schedule_data):
        """
        Add a new schedule

        Args:
            schedule_data: {
                "name": str,
                "profiles": [str],  # List of profile names
                "loops": int,
                "loop_delay_value": int,
                "loop_delay_unit": str,  # "minutes" or "hours"
                "schedule_type": str,  # "once", "daily", "weekly", "interval"
                "schedule_time": str,  # HH:MM format for once/daily/weekly
                "schedule_days": [int],  # Days of week for weekly (0=Monday, 6=Sunday)
                "interval_value": int,  # For interval type
                "interval_unit": str,  # "minutes" or "hours"
                "enabled": bool
            }

        Returns:
            Created schedule with ID
        """
        # Generate unique ID
        max_id = max([s.get('id', 0) for s in self.schedules], default=0)

        schedule = {
            "id": max_id + 1,
            "name": schedule_data.get('name', 'Unnamed Schedule'),
            "profiles": schedule_data.get('profiles', []),
            "loops": schedule_data.get('loops', 1),
            "loop_delay_value": schedule_data.get('loop_delay_value', 0),
            "loop_delay_unit": schedule_data.get('loop_delay_unit', 'minutes'),
            "schedule_type": schedule_data.get('schedule_type', 'once'),
            "schedule_time": schedule_data.get('schedule_time', '00:00'),
            "schedule_days": schedule_data.get('schedule_days', []),
            "interval_value": schedule_data.get('interval_value', 60),
            "interval_unit": schedule_data.get('interval_unit', 'minutes'),
            "enabled": schedule_data.get('enabled', True),
            "created": datetime.now().isoformat(),
            "last_run": None,
            "next_run": None,
            "run_count": 0
        }

        self.schedules.append(schedule)
        self.save_schedules()
        self._calculate_next_run(schedule)

        return schedule

    def update_schedule(self, schedule_id, schedule_data):
        """Update an existing schedule"""
        for schedule in self.schedules:
            if schedule['id'] == schedule_id:
                schedule.update({
                    "name": schedule_data.get('name', schedule['name']),
                    "profiles": schedule_data.get('profiles', schedule['profiles']),
                    "loops": schedule_data.get('loops', schedule['loops']),
                    "loop_delay_value": schedule_data.get('loop_delay_value', schedule.get('loop_delay_value', 0)),
                    "loop_delay_unit": schedule_data.get('loop_delay_unit', schedule.get('loop_delay_unit', 'minutes')),
                    "schedule_type": schedule_data.get('schedule_type', schedule['schedule_type']),
                    "schedule_time": schedule_data.get('schedule_time', schedule['schedule_time']),
                    "schedule_days": schedule_data.get('schedule_days', schedule.get('schedule_days', [])),
                    "interval_value": schedule_data.get('interval_value', schedule.get('interval_value', 60)),
                    "interval_unit": schedule_data.get('interval_unit', schedule.get('interval_unit', 'minutes')),
                    "enabled": schedule_data.get('enabled', schedule['enabled'])
                })
                self.save_schedules()
                self._calculate_next_run(schedule)
                return schedule
        return None

    def delete_schedule(self, schedule_id):
        """Delete a schedule"""
        self.schedules = [s for s in self.schedules if s['id'] != schedule_id]
        if schedule_id in self.next_run_times:
            del self.next_run_times[schedule_id]
        self.save_schedules()

    def toggle_schedule(self, schedule_id, enabled):
        """Enable or disable a schedule"""
        for schedule in self.schedules:
            if schedule['id'] == schedule_id:
                schedule['enabled'] = enabled
                self.save_schedules()
                if enabled:
                    self._calculate_next_run(schedule)
                else:
                    if schedule_id in self.next_run_times:
                        del self.next_run_times[schedule_id]
                    schedule['next_run'] = None
                    self.save_schedules()
                return schedule
        return None

    def _calculate_next_run(self, schedule):
        """Calculate the next run time for a schedule"""
        if not schedule.get('enabled', False):
            return None

        now = datetime.now()
        schedule_type = schedule['schedule_type']

        if schedule_type == 'once':
            # One-time schedule
            time_parts = schedule['schedule_time'].split(':')
            hours = int(time_parts[0])
            minutes = int(time_parts[1])

            next_run = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)

            # If time has passed today, schedule for tomorrow
            if next_run <= now:
                next_run += timedelta(days=1)

            self.next_run_times[schedule['id']] = next_run
            schedule['next_run'] = next_run.isoformat()
            self.save_schedules()
            return next_run

        elif schedule_type == 'daily':
            # Daily schedule
            time_parts = schedule['schedule_time'].split(':')
            hours = int(time_parts[0])
            minutes = int(time_parts[1])

            next_run = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)

            # If time has passed today, schedule for tomorrow
            if next_run <= now:
                next_run += timedelta(days=1)

            self.next_run_times[schedule['id']] = next_run
            schedule['next_run'] = next_run.isoformat()
            self.save_schedules()
            return next_run

        elif schedule_type == 'weekly':
            # Weekly schedule on specific days
            time_parts = schedule['schedule_time'].split(':')
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            schedule_days = schedule.get('schedule_days', [])

            if not schedule_days:
                return None

            # Find next occurrence
            next_run = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)

            # Check if today is a scheduled day and time hasn't passed
            current_weekday = now.weekday()
            if current_weekday in schedule_days and next_run > now:
                self.next_run_times[schedule['id']] = next_run
                schedule['next_run'] = next_run.isoformat()
                self.save_schedules()
                return next_run

            # Find next scheduled day
            for days_ahead in range(1, 8):
                check_date = now + timedelta(days=days_ahead)
                if check_date.weekday() in schedule_days:
                    next_run = check_date.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                    self.next_run_times[schedule['id']] = next_run
                    schedule['next_run'] = next_run.isoformat()
                    self.save_schedules()
                    return next_run

            return None

        elif schedule_type == 'interval':
            # Interval-based schedule
            interval_value = schedule.get('interval_value', 60)
            interval_unit = schedule.get('interval_unit', 'minutes')

            if interval_unit == 'hours':
                delta = timedelta(hours=interval_value)
            else:
                delta = timedelta(minutes=interval_value)

            # If last_run exists, calculate from there; otherwise start from now
            if schedule.get('last_run'):
                last_run = datetime.fromisoformat(schedule['last_run'])
                next_run = last_run + delta
            else:
                next_run = now + delta

            self.next_run_times[schedule['id']] = next_run
            schedule['next_run'] = next_run.isoformat()
            self.save_schedules()
            return next_run

        return None

    def _execute_schedule(self, schedule):
        """Execute a scheduled task"""
        print(f"[SCHEDULER] Executing schedule: {schedule['name']}")

        # Update last_run and run_count
        schedule['last_run'] = datetime.now().isoformat()
        schedule['run_count'] = schedule.get('run_count', 0) + 1

        # Convert loop_delay to seconds
        loop_delay_seconds = 0
        if schedule.get('loop_delay_value', 0) > 0:
            if schedule.get('loop_delay_unit') == 'hours':
                loop_delay_seconds = schedule['loop_delay_value'] * 3600
            else:
                loop_delay_seconds = schedule['loop_delay_value'] * 60

        # Execute the bot
        try:
            self.run_bot_callback(
                selected_profiles=schedule['profiles'],
                loops=schedule['loops'],
                loop_delay_seconds=loop_delay_seconds,
                schedule_id=schedule['id']
            )
        except Exception as e:
            print(f"[SCHEDULER] Error executing schedule {schedule['name']}: {e}")

        # For one-time schedules, disable after execution
        if schedule['schedule_type'] == 'once':
            schedule['enabled'] = False
            schedule['next_run'] = None
            if schedule['id'] in self.next_run_times:
                del self.next_run_times[schedule['id']]
        else:
            # Calculate next run for recurring schedules
            self._calculate_next_run(schedule)

        self.save_schedules()

    def _scheduler_loop(self):
        """Main scheduler loop that runs in background"""
        print("[SCHEDULER] Scheduler started")

        while self.running:
            now = datetime.now()

            # Check each schedule
            for schedule in self.schedules:
                if not schedule.get('enabled', False):
                    continue

                schedule_id = schedule['id']

                # Ensure next_run is calculated
                if schedule_id not in self.next_run_times:
                    self._calculate_next_run(schedule)
                    continue

                next_run = self.next_run_times.get(schedule_id)

                if next_run and now >= next_run:
                    # Time to execute
                    self._execute_schedule(schedule)

            # Sleep for 30 seconds before next check
            time.sleep(30)

        print("[SCHEDULER] Scheduler stopped")

    def start(self):
        """Start the scheduler"""
        if self.running:
            print("[SCHEDULER] Already running")
            return

        # Calculate next run times for all enabled schedules
        for schedule in self.schedules:
            if schedule.get('enabled', False):
                self._calculate_next_run(schedule)

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        print("[SCHEDULER] Started")

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        print("[SCHEDULER] Stopped")

    def get_schedules(self):
        """Get all schedules with updated next_run times"""
        # Refresh next_run times
        for schedule in self.schedules:
            if schedule.get('enabled', False) and schedule['id'] not in self.next_run_times:
                self._calculate_next_run(schedule)

        return self.schedules

    def get_schedule(self, schedule_id):
        """Get a specific schedule"""
        for schedule in self.schedules:
            if schedule['id'] == schedule_id:
                return schedule
        return None
