# Schedule Edit & Select All Update

## New Features Added ✅

### 1. Edit Schedules
You can now edit existing schedules directly from the dashboard!

**How to Edit a Schedule:**
1. Go to the "Schedules" tab
2. Find the schedule you want to edit
3. Click the "Edit" button
4. The form will populate with the schedule's current settings
5. Make your changes
6. Click "Update Schedule" (button changes from "Create" to "Update")
7. Or click "Cancel Edit" to cancel

**What Happens When Editing:**
- Form fields are auto-filled with the schedule's current values
- Profiles are pre-selected
- Days are pre-checked (for weekly schedules)
- Time and interval values are pre-populated
- Submit button changes to "Update Schedule" with green color
- A "Cancel Edit" button appears
- Form scrolls into view automatically

**After Update:**
- Schedule is updated in the backend
- Next run time is recalculated
- Form resets to "Create" mode
- Success message is shown

### 2. Select All Profiles in Schedule Form
The schedule creation form now has a "Select All" checkbox for profiles!

**Features:**
- Highlighted "Select All Profiles" checkbox at the top of the profile list
- Click it to select/deselect all profiles at once
- Visual indicator (blue background and border)
- Automatically updates when individual profiles are checked/unchecked
- Matches the same functionality as the manual run tab

**Visual Design:**
- Blue highlighted background for visibility
- Checkbox syncs with individual profile selections
- Shows "Select All Profiles" in bold blue text

## UI Improvements

### Schedule Actions
Each schedule now has **3 action buttons**:
1. **Edit** - Opens the schedule in the form for editing (NEW!)
2. **Run Now** - Triggers the schedule immediately
3. **Delete** - Removes the schedule

### Form Changes When Editing
- **Button Text**: "Create Schedule" → "Update Schedule"
- **Button Color**: Blue → Green
- **New Button**: "Cancel Edit" appears below the submit button
- **Form State**: All fields populated with current values
- **Scroll Behavior**: Form automatically scrolls into view

### Profile Selection
- **New**: "Select All Profiles" checkbox with blue styling
- **Smart**: Automatically checks/unchecks based on individual selections
- **Consistent**: Same behavior as manual run tab

## How It Works

### Edit Flow
```
1. User clicks "Edit" on a schedule
   ↓
2. Schedule data is fetched from API
   ↓
3. Form fields are populated
   ↓
4. User makes changes
   ↓
5. User clicks "Update Schedule"
   ↓
6. PUT request sent to /api/schedules/{id}
   ↓
7. Schedule updated in backend
   ↓
8. Form resets to create mode
   ↓
9. Schedule list refreshes
```

### Select All Flow
```
1. User clicks "Select All Profiles"
   ↓
2. All profile checkboxes are checked/unchecked
   ↓
3. Individual checkbox changes update "Select All" state
```

## Technical Details

### New JavaScript Functions
- `editSchedule(scheduleId)` - Loads schedule into form for editing
- `resetScheduleForm()` - Clears form and exits edit mode
- `toggleAllScheduleProfiles()` - Selects/deselects all profiles
- `updateScheduleSelectAll()` - Updates select all checkbox state

### Modified Functions
- Form submit handler now checks for `editingScheduleId`
- If editing, sends PUT request instead of POST
- Success message changes based on create vs update

### State Management
- `editingScheduleId` variable tracks which schedule is being edited
- `null` = create mode
- `number` = edit mode for that schedule ID

## Usage Examples

### Example 1: Edit a Daily Schedule
1. You have a "Daily 9 AM" schedule
2. Click "Edit" next to it
3. Change time from 09:00 to 10:00
4. Change profiles selection
5. Click "Update Schedule"
6. Schedule now runs at 10 AM with new profiles

### Example 2: Change Schedule Type
1. You have an "Interval Every 4 Hours" schedule
2. Click "Edit"
3. Change type from "Interval" to "Daily"
4. Set time to 14:00
5. Click "Update Schedule"
6. Schedule now runs daily at 2 PM instead of every 4 hours

### Example 3: Cancel Edit
1. Click "Edit" on any schedule
2. Make some changes
3. Decide you don't want to save
4. Click "Cancel Edit"
5. Form clears and returns to create mode

### Example 4: Select All Profiles
1. Creating a new schedule
2. Have 10 profiles
3. Click "Select All Profiles"
4. All 10 profiles are checked instantly
5. Create schedule with all profiles

## Testing

To test the new features:

1. **Test Edit**:
   ```
   - Create a schedule
   - Click Edit
   - Verify form populates correctly
   - Change some values
   - Click Update Schedule
   - Verify schedule was updated
   ```

2. **Test Cancel Edit**:
   ```
   - Click Edit on a schedule
   - Make changes
   - Click Cancel Edit
   - Verify form clears
   - Verify button says "Create Schedule"
   ```

3. **Test Select All**:
   ```
   - Have multiple profiles
   - Click "Select All Profiles"
   - Verify all are checked
   - Uncheck one manually
   - Verify "Select All" unchecks
   - Check the last one manually
   - Verify "Select All" checks automatically
   ```

## Files Modified

- `static/app.js` - Added edit and select all functionality

## Benefits

✅ **No Need to Delete & Recreate** - Edit schedules in place
✅ **Save Time** - Quickly update schedules without re-entering all data
✅ **Prevent Errors** - Pre-filled values reduce mistakes
✅ **Faster Profile Selection** - Select all with one click
✅ **Better UX** - Visual feedback and smooth workflow
✅ **Consistent Behavior** - Matches manual run tab functionality

## What's Next

You can now:
1. Create schedules
2. Edit schedules ← NEW!
3. Toggle schedules on/off
4. Run schedules immediately
5. Delete schedules
6. Select all profiles easily ← NEW!

Everything you need to manage automated warmup schedules! 🎉
