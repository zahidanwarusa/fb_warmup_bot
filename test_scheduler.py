"""
Test Scheduler - Verify scheduling functionality
Run this script to test if the scheduler is working correctly
"""

import requests
import time
import json
from datetime import datetime

API_BASE = "http://localhost:5000/api"

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}\n")

def test_connection():
    """Test if the Flask app is running"""
    print_header("TEST 1: Connection Test")
    try:
        response = requests.get(f"{API_BASE}/status", timeout=5)
        if response.status_code == 200:
            print("✓ Flask app is running")
            print(f"✓ API is accessible at {API_BASE}")
            return True
        else:
            print(f"✗ Unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Flask app")
        print("  Make sure the app is running: python app.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_get_schedules():
    """Test getting schedules"""
    print_header("TEST 2: Get Schedules")
    try:
        response = requests.get(f"{API_BASE}/schedules")
        if response.status_code == 200:
            schedules = response.json()
            print(f"✓ Successfully fetched schedules")
            print(f"  Current schedule count: {len(schedules)}")
            return True
        else:
            print(f"✗ Failed to get schedules: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_create_schedule():
    """Test creating a schedule"""
    print_header("TEST 3: Create Test Schedule")
    try:
        test_schedule = {
            "name": f"Test Schedule {datetime.now().strftime('%H:%M:%S')}",
            "profiles": ["Test Profile"],
            "loops": 1,
            "schedule_type": "interval",
            "interval_value": 60,
            "interval_unit": "minutes",
            "enabled": False  # Disabled so it won't actually run
        }

        response = requests.post(f"{API_BASE}/schedules", json=test_schedule)
        if response.status_code == 200:
            schedule = response.json()
            print(f"✓ Successfully created schedule")
            print(f"  ID: {schedule['id']}")
            print(f"  Name: {schedule['name']}")
            print(f"  Type: {schedule['schedule_type']}")
            print(f"  Next run: {schedule.get('next_run', 'N/A')}")
            return schedule['id']
        else:
            print(f"✗ Failed to create schedule")
            print(f"  Error: {response.json()}")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_get_schedule(schedule_id):
    """Test getting a specific schedule"""
    print_header("TEST 4: Get Specific Schedule")
    try:
        response = requests.get(f"{API_BASE}/schedules/{schedule_id}")
        if response.status_code == 200:
            schedule = response.json()
            print(f"✓ Successfully retrieved schedule {schedule_id}")
            print(f"  Name: {schedule['name']}")
            print(f"  Enabled: {schedule['enabled']}")
            return True
        else:
            print(f"✗ Failed to get schedule: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_toggle_schedule(schedule_id):
    """Test toggling a schedule"""
    print_header("TEST 5: Toggle Schedule")
    try:
        # Enable it
        response = requests.post(
            f"{API_BASE}/schedules/{schedule_id}/toggle",
            json={"enabled": True}
        )
        if response.status_code == 200:
            print(f"✓ Successfully enabled schedule {schedule_id}")

            # Disable it
            response = requests.post(
                f"{API_BASE}/schedules/{schedule_id}/toggle",
                json={"enabled": False}
            )
            if response.status_code == 200:
                print(f"✓ Successfully disabled schedule {schedule_id}")
                return True
            else:
                print(f"✗ Failed to disable schedule")
                return False
        else:
            print(f"✗ Failed to enable schedule")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_update_schedule(schedule_id):
    """Test updating a schedule"""
    print_header("TEST 6: Update Schedule")
    try:
        update_data = {
            "name": f"Updated Test Schedule {datetime.now().strftime('%H:%M:%S')}",
            "loops": 2
        }

        response = requests.put(
            f"{API_BASE}/schedules/{schedule_id}",
            json=update_data
        )
        if response.status_code == 200:
            schedule = response.json()
            print(f"✓ Successfully updated schedule {schedule_id}")
            print(f"  New name: {schedule['name']}")
            print(f"  New loops: {schedule['loops']}")
            return True
        else:
            print(f"✗ Failed to update schedule")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_delete_schedule(schedule_id):
    """Test deleting a schedule"""
    print_header("TEST 7: Delete Schedule")
    try:
        response = requests.delete(f"{API_BASE}/schedules/{schedule_id}")
        if response.status_code == 200:
            print(f"✓ Successfully deleted schedule {schedule_id}")

            # Verify it's gone
            response = requests.get(f"{API_BASE}/schedules/{schedule_id}")
            if response.status_code == 404:
                print(f"✓ Verified schedule was deleted")
                return True
            else:
                print(f"✗ Schedule still exists after deletion")
                return False
        else:
            print(f"✗ Failed to delete schedule")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_schedule_types():
    """Test creating different schedule types"""
    print_header("TEST 8: Schedule Types")

    types = [
        {
            "name": "Test Daily",
            "schedule_type": "daily",
            "schedule_time": "09:00"
        },
        {
            "name": "Test Weekly",
            "schedule_type": "weekly",
            "schedule_time": "10:00",
            "schedule_days": [0, 1, 2, 3, 4]
        },
        {
            "name": "Test Once",
            "schedule_type": "once",
            "schedule_time": "15:00"
        },
        {
            "name": "Test Interval",
            "schedule_type": "interval",
            "interval_value": 30,
            "interval_unit": "minutes"
        }
    ]

    created_ids = []

    for schedule_type in types:
        try:
            data = {
                "name": schedule_type["name"],
                "profiles": ["Test Profile"],
                "loops": 1,
                "enabled": False,
                **schedule_type
            }

            response = requests.post(f"{API_BASE}/schedules", json=data)
            if response.status_code == 200:
                schedule = response.json()
                print(f"✓ Created {schedule_type['schedule_type']} schedule (ID: {schedule['id']})")
                created_ids.append(schedule['id'])
            else:
                print(f"✗ Failed to create {schedule_type['schedule_type']} schedule")
                print(f"  Error: {response.json()}")
        except Exception as e:
            print(f"✗ Error creating {schedule_type['schedule_type']}: {e}")

    # Clean up
    print(f"\nCleaning up test schedules...")
    for schedule_id in created_ids:
        try:
            requests.delete(f"{API_BASE}/schedules/{schedule_id}")
        except:
            pass

    print(f"✓ Deleted {len(created_ids)} test schedules")
    return len(created_ids) == 4

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("FACEBOOK WARMUP BOT - SCHEDULER TEST SUITE".center(70))
    print("="*70)

    results = []

    # Test 1: Connection
    if test_connection():
        results.append(("Connection", True))
    else:
        results.append(("Connection", False))
        print("\n✗ Cannot proceed without connection to Flask app")
        print_results(results)
        return

    # Test 2: Get schedules
    if test_get_schedules():
        results.append(("Get Schedules", True))
    else:
        results.append(("Get Schedules", False))

    # Test 3: Create schedule
    schedule_id = test_create_schedule()
    if schedule_id:
        results.append(("Create Schedule", True))

        # Test 4: Get specific schedule
        if test_get_schedule(schedule_id):
            results.append(("Get Schedule", True))
        else:
            results.append(("Get Schedule", False))

        # Test 5: Toggle schedule
        if test_toggle_schedule(schedule_id):
            results.append(("Toggle Schedule", True))
        else:
            results.append(("Toggle Schedule", False))

        # Test 6: Update schedule
        if test_update_schedule(schedule_id):
            results.append(("Update Schedule", True))
        else:
            results.append(("Update Schedule", False))

        # Test 7: Delete schedule
        if test_delete_schedule(schedule_id):
            results.append(("Delete Schedule", True))
        else:
            results.append(("Delete Schedule", False))
    else:
        results.append(("Create Schedule", False))

    # Test 8: Schedule types
    if test_schedule_types():
        results.append(("Schedule Types", True))
    else:
        results.append(("Schedule Types", False))

    # Print results
    print_results(results)

def print_results(results):
    """Print test results summary"""
    print_header("TEST RESULTS SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {test_name}")

    print(f"\n{'='*70}")
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! Scheduler is working correctly.")
    else:
        print(f"\n✗ {total - passed} test(s) failed. Check the output above for details.")

    print(f"{'='*70}\n")

if __name__ == "__main__":
    run_all_tests()
