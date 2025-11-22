// Add new task
document.getElementById('taskForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const taskName = document.getElementById('taskName').value;
    const taskAmount = parseFloat(document.getElementById('taskAmount').value);
    
    // Convert 12-hour time to 24-hour format
    const convertTo24Hour = (hour, min, period) => {
        if (!hour || !min) return '';
        let h = parseInt(hour);
        if (period === 'PM' && h !== 12) h += 12;
        if (period === 'AM' && h === 12) h = 0;
        return `${h.toString().padStart(2, '0')}:${min}`;
    };
    
    const timeFromHour = document.getElementById('timeFromHour').value;
    const timeFromMin = document.getElementById('timeFromMin').value;
    const timeFromPeriod = document.getElementById('timeFromPeriod').value;
    const timeFrom = convertTo24Hour(timeFromHour, timeFromMin, timeFromPeriod);
    
    const timeToHour = document.getElementById('timeToHour').value;
    const timeToMin = document.getElementById('timeToMin').value;
    const timeToPeriod = document.getElementById('timeToPeriod').value;
    const timeTo = convertTo24Hour(timeToHour, timeToMin, timeToPeriod);
    
    const body = {task_name: taskName, amount: taskAmount};
    if (timeFrom) body.time_from = timeFrom;
    if (timeTo) body.time_to = timeTo;
    
    const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
    });
    
    if (response.ok) {
        location.reload();
    }
});

// Toggle task completion
document.querySelectorAll('.task-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', async (e) => {
        const taskId = e.target.dataset.id;
        const response = await fetch(`/api/tasks/${taskId}/toggle`, {
            method: 'PUT'
        });
        
        if (response.ok) {
            location.reload();
        }
    });
});

// Delete task
document.querySelectorAll('.delete-btn, .delete-btn-small').forEach(button => {
    button.addEventListener('click', async (e) => {
        const taskId = e.target.dataset.id;
        if (confirm('Are you sure you want to delete this task?')) {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                location.reload();
            }
        }
    });
});

// Animate progress circle
window.addEventListener('DOMContentLoaded', () => {
    const progressText = document.getElementById('progressText');
    const progressBar = document.getElementById('progressBar');
    
    if (progressText && progressBar) {
        const text = progressText.textContent;
        const [completed, total] = text.split('/').map(n => parseInt(n));
        
        if (total > 0) {
            const percentage = completed / total;
            const circumference = 2 * Math.PI * 50; // radius is 50
            const offset = circumference - (percentage * circumference);
            
            progressBar.style.strokeDashoffset = offset;
        }
    }
});
