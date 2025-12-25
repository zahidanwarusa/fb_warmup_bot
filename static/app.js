// Facebook Warmup Bot - Frontend JavaScript
// Handles both manual runs and schedule management

const API_URL = window.location.origin;
let statusInterval = null;
let lastDelayRemaining = 0;
let totalDelaySeconds = 0;

// ========== INITIALIZATION ==========

document.addEventListener('DOMContentLoaded', () => {
    loadProfiles();
    loadSchedules();
    startStatusPolling();
    populateScheduleProfiles();
});

// ========== TAB SWITCHING ==========

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    if (tabName === 'manual') {
        document.getElementById('manualTab').classList.add('active');
    } else if (tabName === 'schedules') {
        document.getElementById('schedulesTab').classList.add('active');
        loadSchedules(); // Refresh schedules when switching to tab
    }
}

// ========== PROFILE MANAGEMENT ==========

async function loadProfiles() {
    try {
        const response = await fetch(`${API_URL}/api/profiles`);
        const profiles = await response.json();

        const profileList = document.getElementById('profileList');

        if (profiles.length === 0) {
            profileList.innerHTML = `
                <div class="empty-state">
                    <span class="icon-large">[ ]</span>
                    <p>No profiles added yet.<br>Add your first profile above.</p>
                </div>
            `;
            return;
        }

        profileList.innerHTML = profiles.map(profile => `
            <div class="profile-item" data-id="${profile.id}" data-name="${profile.name}">
                <input type="checkbox" class="profile-checkbox" value="${profile.name}">
                <div class="profile-info">
                    <div class="profile-name">${profile.name}</div>
                    <div class="profile-path">${profile.path}</div>
                </div>
                <div class="profile-actions">
                    <button class="btn-edit" onclick="editProfile(${profile.id})">Edit</button>
                    <button class="btn-delete" onclick="deleteProfile(${profile.id})">Delete</button>
                </div>
            </div>
        `).join('');

        updateSelectAll();
        populateScheduleProfiles(); // Update schedule form checkboxes
    } catch (error) {
        console.error('Error loading profiles:', error);
    }
}

document.getElementById('addProfileForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('profileName').value.trim();
    const path = document.getElementById('profilePath').value.trim();

    if (!name || !path) {
        alert('Please fill in all fields');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/profiles`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, path })
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('profileName').value = '';
            document.getElementById('profilePath').value = '';
            loadProfiles();
            addLog(`Profile added: ${name}`, 'success');
        } else {
            alert(data.error || 'Failed to add profile');
        }
    } catch (error) {
        console.error('Error adding profile:', error);
        alert('Failed to connect to server');
    }
});

async function deleteProfile(id) {
    if (!confirm('Are you sure you want to delete this profile?')) return;

    try {
        await fetch(`${API_URL}/api/profiles/${id}`, { method: 'DELETE' });
        loadProfiles();
        addLog('Profile deleted', 'info');
    } catch (error) {
        console.error('Error deleting profile:', error);
    }
}

async function editProfile(id) {
    const item = document.querySelector(`[data-id="${id}"]`);
    const currentName = item.querySelector('.profile-name').textContent;
    const currentPath = item.querySelector('.profile-path').textContent;

    const newName = prompt('Enter new profile name:', currentName);
    if (newName === null) return;

    const newPath = prompt('Enter new profile path:', currentPath);
    if (newPath === null) return;

    try {
        await fetch(`${API_URL}/api/profiles/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName, path: newPath })
        });
        loadProfiles();
        addLog('Profile updated', 'info');
    } catch (error) {
        console.error('Error updating profile:', error);
    }
}

document.getElementById('selectAll').addEventListener('change', async (e) => {
    if (e.target.checked) {
        try {
            const statusResponse = await fetch(`${API_URL}/api/status`);
            const status = await statusResponse.json();

            if (status.completed.length > 0 || status.failed.length > 0) {
                await fetch(`${API_URL}/api/reset`, { method: 'POST' });
                await loadProfiles();

                setTimeout(() => {
                    const checkboxes = document.querySelectorAll('.profile-item .profile-checkbox');
                    checkboxes.forEach(cb => cb.checked = true);
                    document.getElementById('selectAll').checked = true;
                    document.getElementById('runBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                }, 100);

                const logConsole = document.getElementById('logConsole');
                logConsole.innerHTML = '<div class="log-entry info">Status auto-reset. All profiles ready for new run.</div>';

                document.getElementById('queueSection').style.display = 'none';
                document.getElementById('delayPanel').style.display = 'none';

                addLog('Status auto-reset. All profiles selected and ready.', 'info');
                return;
            }
        } catch (error) {
            console.error('Error checking status:', error);
        }
    }

    const checkboxes = document.querySelectorAll('.profile-item .profile-checkbox');
    checkboxes.forEach(cb => cb.checked = e.target.checked);
});

function updateSelectAll() {
    const checkboxes = document.querySelectorAll('.profile-item .profile-checkbox');
    const selectAll = document.getElementById('selectAll');

    if (checkboxes.length === 0) {
        selectAll.checked = false;
        return;
    }

    selectAll.checked = Array.from(checkboxes).every(cb => cb.checked);
}

document.getElementById('profileList').addEventListener('change', (e) => {
    if (e.target.classList.contains('profile-checkbox')) {
        updateSelectAll();
    }
});

// ========== BOT CONTROLS ==========

async function runBot() {
    const checkboxes = document.querySelectorAll('.profile-item .profile-checkbox:checked');
    const selectedProfiles = Array.from(checkboxes).map(cb => cb.value);
    const loopCount = parseInt(document.getElementById('loopCount').value) || 1;
    const loopDelayValue = parseInt(document.getElementById('loopDelayValue').value) || 0;
    const loopDelayUnit = document.getElementById('loopDelayUnit').value;

    if (selectedProfiles.length === 0) {
        alert('Please select at least one profile');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                profiles: selectedProfiles,
                loops: loopCount,
                loop_delay_value: loopDelayValue,
                loop_delay_unit: loopDelayUnit
            })
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('runBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            document.getElementById('queueSection').style.display = 'block';

            if (loopDelayUnit === 'hours') {
                totalDelaySeconds = loopDelayValue * 3600;
            } else {
                totalDelaySeconds = loopDelayValue * 60;
            }

            addLog(`Started queue: ${selectedProfiles.length} profile(s) x ${loopCount} round(s)`, 'success');
        } else {
            alert(data.error || 'Failed to start bot');
        }
    } catch (error) {
        console.error('Error running bot:', error);
        alert('Failed to connect to server');
    }
}

async function stopBot() {
    try {
        await fetch(`${API_URL}/api/stop`, { method: 'POST' });
        addLog('Stop requested - will stop after current task', 'error');
    } catch (error) {
        console.error('Error stopping bot:', error);
    }
}

async function resetStatus() {
    try {
        const response = await fetch(`${API_URL}/api/reset`, { method: 'POST' });
        const data = await response.json();

        if (response.ok) {
            loadProfiles();
            document.getElementById('runBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('queueSection').style.display = 'none';
            document.getElementById('delayPanel').style.display = 'none';

            const logConsole = document.getElementById('logConsole');
            logConsole.innerHTML = '<div class="log-entry info">Ready to start...</div>';

            addLog('Status reset', 'info');
        } else {
            alert(data.error || 'Failed to reset');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// ========== STATUS POLLING ==========

function startStatusPolling() {
    if (statusInterval) clearInterval(statusInterval);
    statusInterval = setInterval(updateStatus, 1000);
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

async function updateStatus() {
    try {
        const response = await fetch(`${API_URL}/api/status`);
        const status = await response.json();

        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');

        statusDot.className = 'status-dot';

        if (status.is_delaying) {
            statusDot.classList.add('delaying');
            statusText.textContent = `Waiting between rounds (${formatTime(status.delay_remaining)})`;
            document.getElementById('delayPanel').style.display = 'block';
            document.getElementById('currentTaskPanel').style.display = 'none';

            document.getElementById('delayCountdown').textContent = formatTime(status.delay_remaining);

            if (totalDelaySeconds > 0) {
                const progress = ((totalDelaySeconds - status.delay_remaining) / totalDelaySeconds) * 100;
                document.getElementById('delayProgressBar').style.width = `${progress}%`;
            }
        } else {
            document.getElementById('delayPanel').style.display = 'none';

            if (status.running) {
                statusDot.classList.add('running');
                statusText.textContent = `Running: ${status.current_profile || '...'} (Round ${status.current_round || 1})`;
                document.getElementById('runBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
            } else {
                const completedCount = status.queue.filter(q => q.status === 'completed').length;
                const failedCount = status.queue.filter(q => q.status === 'failed').length;

                if (completedCount > 0 || failedCount > 0) {
                    statusDot.classList.add('completed');
                    statusText.textContent = `Done (${completedCount} success, ${failedCount} failed)`;
                } else {
                    statusDot.classList.add('idle');
                    statusText.textContent = 'Idle';
                }
                document.getElementById('runBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            }
        }

        const taskPanel = document.getElementById('currentTaskPanel');
        const currentTask = document.getElementById('currentTask');

        if (status.running && status.current_task && !status.is_delaying) {
            taskPanel.style.display = 'block';
            currentTask.textContent = status.current_task;
        } else {
            taskPanel.style.display = 'none';
        }

        if (status.queue && status.queue.length > 0) {
            document.getElementById('queueSection').style.display = 'block';
            updateQueueDisplay(status.queue, status.current_queue_index);
        }

        const profileItems = document.querySelectorAll('.profile-item');
        profileItems.forEach(item => {
            const name = item.dataset.name;
            item.classList.remove('running', 'completed', 'failed');

            const oldBadge = item.querySelector('.profile-status');
            if (oldBadge) oldBadge.remove();

            if (status.current_profile === name && status.running) {
                item.classList.add('running');
                item.querySelector('.profile-info').innerHTML +=
                    `<span class="profile-status status-running">Running (R${status.current_round || 1})</span>`;
            }
        });

        if (status.logs && status.logs.length > 0) {
            const logConsole = document.getElementById('logConsole');
            logConsole.innerHTML = status.logs.map(log => {
                let className = '';
                if (log.includes('SUCCESS')) className = 'success';
                else if (log.includes('ERROR') || log.includes('FAILED')) className = 'error';
                else if (log.includes('STARTING') || log.includes('===') || log.includes('INFO')) className = 'info';

                return `<div class="log-entry ${className}">${log}</div>`;
            }).join('');
            logConsole.scrollTop = logConsole.scrollHeight;
        }

    } catch (error) {
        console.error('Status update error:', error);
    }
}

function updateQueueDisplay(queue, currentIndex) {
    const queueList = document.getElementById('queueList');
    const queueStats = document.getElementById('queueStats');
    const progressBar = document.getElementById('queueProgressBar');

    const pending = queue.filter(q => q.status === 'pending').length;
    const running = queue.filter(q => q.status === 'running').length;
    const completed = queue.filter(q => q.status === 'completed').length;
    const failed = queue.filter(q => q.status === 'failed').length;
    const skipped = queue.filter(q => q.status === 'skipped').length;

    queueStats.innerHTML = `
        <span class="queue-stat pending">Pending: ${pending}</span>
        <span class="queue-stat completed">Completed: ${completed}</span>
        <span class="queue-stat failed">Failed: ${failed}</span>
        ${skipped > 0 ? `<span class="queue-stat skipped">Skipped: ${skipped}</span>` : ''}
    `;

    const progress = ((completed + failed + skipped) / queue.length) * 100;
    progressBar.style.width = `${progress}%`;

    queueList.innerHTML = queue.map((item, index) => {
        let icon = '○';
        if (item.status === 'running') icon = '▶';
        else if (item.status === 'completed') icon = '✓';
        else if (item.status === 'failed') icon = '✗';
        else if (item.status === 'skipped') icon = '⊘';

        return `
            <div class="queue-item ${item.status}">
                <span class="queue-item-icon">${icon}</span>
                <span class="queue-item-info">${item.profile} - Round ${item.round}</span>
                <span class="queue-item-status">${item.status}</span>
            </div>
        `;
    }).join('');
}

// ========== LOGS ==========

function addLog(message, type = '') {
    const logConsole = document.getElementById('logConsole');
    const timestamp = new Date().toLocaleTimeString();
    logConsole.innerHTML += `<div class="log-entry ${type}">[${timestamp}] ${message}</div>`;
    logConsole.scrollTop = logConsole.scrollHeight;
}

function copyLogs() {
    const logConsole = document.getElementById('logConsole');
    const logs = Array.from(logConsole.querySelectorAll('.log-entry'))
        .map(entry => entry.textContent)
        .join('\n');

    navigator.clipboard.writeText(logs).then(() => {
        const notification = document.getElementById('copyNotification');
        notification.classList.add('show');
        setTimeout(() => notification.classList.remove('show'), 2000);
    });
}

async function clearLogs() {
    try {
        await fetch(`${API_URL}/api/clear-logs`, { method: 'POST' });
    } catch (error) {
        console.error('Error clearing server logs:', error);
    }

    const logConsole = document.getElementById('logConsole');
    logConsole.innerHTML = '<div class="log-entry info">Logs cleared</div>';
}

// ========== SCHEDULING ==========

async function loadSchedules() {
    try {
        const response = await fetch(`${API_URL}/api/schedules`);
        const schedules = await response.json();

        const scheduleList = document.getElementById('scheduleList');

        if (schedules.length === 0) {
            scheduleList.innerHTML = `
                <div class="empty-state">
                    <span class="icon-large">⏰</span>
                    <p>No schedules created yet.<br>Create your first schedule.</p>
                </div>
            `;
            return;
        }

        scheduleList.innerHTML = schedules.map(schedule => {
            const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
            let details = '';

            if (schedule.schedule_type === 'daily') {
                details = `Daily at ${schedule.schedule_time}`;
            } else if (schedule.schedule_type === 'weekly') {
                const days = schedule.schedule_days.map(d => dayNames[d]).join(', ');
                details = `${days} at ${schedule.schedule_time}`;
            } else if (schedule.schedule_type === 'interval') {
                details = `Every ${schedule.interval_value} ${schedule.interval_unit}`;
            } else if (schedule.schedule_type === 'once') {
                details = `Once at ${schedule.schedule_time}`;
            }

            const nextRun = schedule.next_run ? new Date(schedule.next_run).toLocaleString() : 'Not scheduled';

            return `
                <div class="schedule-item ${schedule.enabled ? '' : 'disabled'}">
                    <div class="schedule-toggle ${schedule.enabled ? 'enabled' : ''}"
                         onclick="toggleSchedule(${schedule.id}, ${!schedule.enabled})">
                    </div>
                    <div class="schedule-info">
                        <div class="schedule-name">${schedule.name}</div>
                        <div class="schedule-details">
                            ${details} | ${schedule.profiles.length} profile(s) | ${schedule.loops} round(s)
                        </div>
                        <div class="schedule-next-run">
                            Next run: ${nextRun} | Runs: ${schedule.run_count || 0}
                        </div>
                    </div>
                    <div class="schedule-actions">
                        <button class="btn-edit btn-small" onclick="runScheduleNow(${schedule.id})">Run Now</button>
                        <button class="btn-delete btn-small" onclick="deleteSchedule(${schedule.id})">Delete</button>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading schedules:', error);
    }
}

async function populateScheduleProfiles() {
    try {
        const response = await fetch(`${API_URL}/api/profiles`);
        const profiles = await response.json();

        const container = document.getElementById('scheduleProfilesList');

        if (profiles.length === 0) {
            container.innerHTML = '<p style="color: #8892b0; padding: 10px;">No profiles available. Add profiles first.</p>';
            return;
        }

        container.innerHTML = profiles.map(profile => `
            <label style="display: flex; align-items: center; gap: 10px; padding: 8px; cursor: pointer;">
                <input type="checkbox" class="schedule-profile-checkbox" value="${profile.name}" style="width: auto;">
                <span>${profile.name}</span>
            </label>
        `).join('');
    } catch (error) {
        console.error('Error loading profiles for schedule:', error);
    }
}

function updateScheduleFields() {
    const scheduleType = document.getElementById('scheduleType').value;

    const timeGroup = document.getElementById('scheduleTimeGroup');
    const daysGroup = document.getElementById('scheduleDaysGroup');
    const intervalGroup = document.getElementById('scheduleIntervalGroup');

    timeGroup.style.display = 'none';
    daysGroup.style.display = 'none';
    intervalGroup.style.display = 'none';

    if (scheduleType === 'daily' || scheduleType === 'once') {
        timeGroup.style.display = 'block';
    } else if (scheduleType === 'weekly') {
        timeGroup.style.display = 'block';
        daysGroup.style.display = 'block';
    } else if (scheduleType === 'interval') {
        intervalGroup.style.display = 'block';
    }
}

document.getElementById('addScheduleForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('scheduleName').value.trim();
    const scheduleType = document.getElementById('scheduleType').value;
    const loops = parseInt(document.getElementById('scheduleLoops').value) || 1;
    const delayValue = parseInt(document.getElementById('scheduleDelayValue').value) || 0;
    const delayUnit = document.getElementById('scheduleDelayUnit').value;

    const profileCheckboxes = document.querySelectorAll('.schedule-profile-checkbox:checked');
    const profiles = Array.from(profileCheckboxes).map(cb => cb.value);

    if (!name) {
        alert('Please enter a schedule name');
        return;
    }

    if (profiles.length === 0) {
        alert('Please select at least one profile');
        return;
    }

    const scheduleData = {
        name,
        profiles,
        loops,
        loop_delay_value: delayValue,
        loop_delay_unit: delayUnit,
        schedule_type: scheduleType,
        enabled: true
    };

    if (scheduleType === 'daily' || scheduleType === 'weekly' || scheduleType === 'once') {
        scheduleData.schedule_time = document.getElementById('scheduleTime').value;
    }

    if (scheduleType === 'weekly') {
        const dayCheckboxes = document.querySelectorAll('#scheduleDaysGroup input:checked');
        scheduleData.schedule_days = Array.from(dayCheckboxes).map(cb => parseInt(cb.value));

        if (scheduleData.schedule_days.length === 0) {
            alert('Please select at least one day for weekly schedule');
            return;
        }
    }

    if (scheduleType === 'interval') {
        scheduleData.interval_value = parseInt(document.getElementById('intervalValue').value) || 60;
        scheduleData.interval_unit = document.getElementById('intervalUnit').value;
    }

    try {
        const response = await fetch(`${API_URL}/api/schedules`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(scheduleData)
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('addScheduleForm').reset();
            document.getElementById('scheduleTime').value = '09:00';
            loadSchedules();
            alert(`Schedule "${name}" created successfully!`);
        } else {
            alert(data.error || 'Failed to create schedule');
        }
    } catch (error) {
        console.error('Error creating schedule:', error);
        alert('Failed to connect to server');
    }
});

async function toggleSchedule(scheduleId, enabled) {
    try {
        const response = await fetch(`${API_URL}/api/schedules/${scheduleId}/toggle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled })
        });

        if (response.ok) {
            loadSchedules();
        } else {
            alert('Failed to toggle schedule');
        }
    } catch (error) {
        console.error('Error toggling schedule:', error);
    }
}

async function deleteSchedule(scheduleId) {
    if (!confirm('Are you sure you want to delete this schedule?')) return;

    try {
        const response = await fetch(`${API_URL}/api/schedules/${scheduleId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadSchedules();
        } else {
            alert('Failed to delete schedule');
        }
    } catch (error) {
        console.error('Error deleting schedule:', error);
    }
}

async function runScheduleNow(scheduleId) {
    if (!confirm('Run this schedule immediately?')) return;

    try {
        const response = await fetch(`${API_URL}/api/schedules/${scheduleId}/run-now`, {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            // Switch to manual tab to see execution
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab')[0].classList.add('active');
            document.getElementById('manualTab').classList.add('active');
            document.getElementById('schedulesTab').classList.remove('active');

            alert(data.message || 'Schedule triggered successfully');
        } else {
            alert(data.error || 'Failed to run schedule');
        }
    } catch (error) {
        console.error('Error running schedule:', error);
        alert('Failed to connect to server');
    }
}

// Initialize schedule type fields
updateScheduleFields();
