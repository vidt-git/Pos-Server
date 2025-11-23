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

// Done Tasks Modal Functions
async function openDoneTasksModal() {
    const modal = document.getElementById('doneTasksModal');
    const container = document.getElementById('doneTasksContainer');
    
    modal.style.display = 'block';
    container.innerHTML = '<div class="loading">Loading...</div>';
    
    try {
        const response = await fetch('/api/done-tasks');
        const data = await response.json();
        const doneTasks = data.done_tasks;
        
        if (doneTasks.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">✅</div><div>No completed tasks</div></div>';
            return;
        }
        
        // Sort by completed_at descending (most recent first)
        doneTasks.sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at));
        
        let html = '';
        doneTasks.forEach(task => {
            const completedDate = new Date(task.completed_at).toLocaleString('en-US', {
                month: '2-digit',
                day: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            const createdDate = new Date(task.created_at).toLocaleDateString('en-US', {
                month: '2-digit',
                day: '2-digit',
                year: 'numeric'
            });
            
            html += `
                <div class="done-task-card" data-task-id="${task.id}">
                    <div class="done-task-info">
                        <div class="done-task-name">${task.task_name}</div>
                        <div class="done-task-meta">
                            <span>Created: ${createdDate}</span>
                            <span>Completed: ${completedDate}</span>
                        </div>
                    </div>
                    <div class="done-task-right">
                        <div class="done-task-amount">₹${task.amount.toFixed(2)}</div>
                        <button class="done-task-delete" onclick="deleteDoneTask(${task.id})">🗑️</button>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<div class="empty-state"><div style="color: #ff6b4a;">Error loading tasks</div></div>';
        console.error('Error fetching done tasks:', error);
    }
}

function closeDoneTasksModal() {
    document.getElementById('doneTasksModal').style.display = 'none';
}

async function deleteDoneTask(taskId) {
    if (!confirm('Are you sure you want to delete this completed task?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/done-tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // Remove the card from the modal
            const card = document.querySelector(`[data-task-id="${taskId}"]`);
            if (card) {
                card.style.opacity = '0';
                card.style.transform = 'translateX(-20px)';
                setTimeout(() => {
                    card.remove();
                    // Check if there are any tasks left
                    const container = document.getElementById('doneTasksContainer');
                    if (container.children.length === 0) {
                        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">✅</div><div>No completed tasks</div></div>';
                    }
                }, 300);
            }
            
            // Reload the page to update running total
            setTimeout(() => location.reload(), 500);
        }
    } catch (error) {
        alert('Error deleting task');
        console.error('Error deleting done task:', error);
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('doneTasksModal');
    if (event.target === modal) {
        closeDoneTasksModal();
    }
};
