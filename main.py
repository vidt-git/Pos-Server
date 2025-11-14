from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import json
import os
from threading import Lock

# JSON file paths
TODO_FILE = "TodoTasks.json"
DONE_FILE = "DoneTodo.json"

# Thread lock for file operations
file_lock = Lock()

app = FastAPI()

# Pydantic models
class TaskCreate(BaseModel):
    task_name: str
    amount: float

class Task(BaseModel):
    id: int
    task_name: str
    amount: float
    created_at: str
    date: str  # Date in YYYY-MM-DD format for filtering

class DoneTask(BaseModel):
    id: int
    task_name: str
    amount: float
    created_at: str
    completed_at: str
    date: str

# Helper functions
def load_json_file(filepath: str) -> List:
    """Load JSON file, return empty list if not exists"""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return []

def save_json_file(filepath: str, data: List):
    """Save data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def get_next_id(tasks: List) -> int:
    """Get next available ID"""
    if not tasks:
        return 1
    return max(task['id'] for task in tasks) + 1

def get_today_date() -> str:
    """Get today's date in YYYY-MM-DD format"""
    return datetime.now().strftime("%Y-%m-%d")

def get_running_total() -> float:
    """Calculate running total from completed tasks"""
    with file_lock:
        done_tasks = load_json_file(DONE_FILE)
        return sum(task['amount'] for task in done_tasks)

def render_page():
    """Render todo list page"""
    with file_lock:
        todo_tasks = load_json_file(TODO_FILE)
        done_tasks = load_json_file(DONE_FILE)
        running_total = sum(task['amount'] for task in done_tasks)
    
    today = get_today_date()
    
    # Filter tasks for today
    today_tasks = [t for t in todo_tasks if t['date'] == today]
    
    # Create a set of done task IDs for quick lookup
    done_task_ids = {t['id'] for t in done_tasks}
    
    tasks_html = ""
    for task in today_tasks:
        is_done = task['id'] in done_task_ids
        checked = "checked" if is_done else ""
        task_class = "done" if is_done else ""
        
        created_dt = datetime.fromisoformat(task['created_at'])
        created_date = created_dt.strftime("%m/%d %I:%M%p")
        
        completed_date = ""
        if is_done:
            done_task = next((t for t in done_tasks if t['id'] == task['id']), None)
            if done_task:
                completed_dt = datetime.fromisoformat(done_task['completed_at'])
                completed_date = completed_dt.strftime("%m/%d %I:%M%p")
        
        tasks_html += f"""
        <div class="task-item {task_class}">
            <div class="task-left">
                <input type="checkbox" class="task-checkbox" data-id="{task['id']}" {checked}>
                <div class="task-info">
                    <div class="task-name">{task['task_name']}</div>
                    <div class="task-date">Created: {created_date}{f" | Done: {completed_date}" if completed_date else ""}</div>
                </div>
            </div>
            <div class="task-right">
                <div class="task-amount">₹{task['amount']:.2f}</div>
                <button class="delete-btn" data-id="{task['id']}">🗑️</button>
            </div>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Task Manager</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #9b59b6 0%, #6c3483 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(107, 52, 131, 0.3);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #8e44ad 0%, #6c3483 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            
            h1 {{
                font-size: 2.5em;
                font-weight: 700;
            }}
            
            .total-section {{
                background: #7d3c98;
                color: white;
                padding: 20px 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 3px solid #6c3483;
            }}
            
            .total-label {{
                font-size: 1.2em;
                font-weight: 500;
            }}
            
            .total-amount {{
                font-size: 2em;
                font-weight: 700;
            }}
            
            .add-task-section {{
                padding: 30px;
                background: #f9f9f9;
                border-bottom: 2px solid #e8e8e8;
            }}
            
            .form-row {{
                display: flex;
                gap: 15px;
                margin-bottom: 15px;
            }}
            
            input[type="text"],
            input[type="number"] {{
                flex: 1;
                padding: 12px 15px;
                border: 2px solid #d4b8e8;
                border-radius: 10px;
                font-size: 1em;
                font-family: 'Inter', sans-serif;
                background: white;
                transition: border-color 0.3s;
            }}
            
            input[type="text"]:focus,
            input[type="number"]:focus {{
                outline: none;
                border-color: #8e44ad;
            }}
            
            .add-btn {{
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #8e44ad 0%, #6c3483 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 1.1em;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .add-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(142, 68, 173, 0.4);
            }}
            
            .add-btn:active {{
                transform: translateY(0);
            }}
            
            .tasks-section {{
                padding: 20px 30px;
                max-height: 500px;
                overflow-y: auto;
            }}
            
            .task-item {{
                background: white;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 12px;
                border: 2px solid #e8d8f5;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: all 0.3s;
            }}
            
            .task-item:hover {{
                box-shadow: 0 4px 12px rgba(142, 68, 173, 0.2);
                transform: translateY(-2px);
            }}
            
            .task-item.done {{
                background: #f5f0f8;
                opacity: 0.7;
                border-color: #d4b8e8;
            }}
            
            .task-left {{
                display: flex;
                align-items: center;
                gap: 15px;
                flex: 1;
            }}
            
            .task-checkbox {{
                width: 24px;
                height: 24px;
                cursor: pointer;
                accent-color: #8e44ad;
            }}
            
            .task-info {{
                flex: 1;
            }}
            
            .task-name {{
                font-size: 1.1em;
                color: #333;
                margin-bottom: 5px;
                font-weight: 500;
            }}
            
            .task-item.done .task-name {{
                text-decoration: line-through;
            }}
            
            .task-date {{
                font-size: 0.8em;
                color: #888;
            }}
            
            .task-right {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .task-amount {{
                font-size: 1.3em;
                font-weight: 700;
                color: #8e44ad;
            }}
            
            .delete-btn {{
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                cursor: pointer;
                font-size: 1.2em;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .delete-btn:hover {{
                background: #c0392b;
                transform: scale(1.1);
            }}
            
            .delete-btn:active {{
                transform: scale(0.95);
            }}
            
            .empty-state {{
                text-align: center;
                padding: 40px;
                color: #888;
            }}
            
            .empty-state-icon {{
                font-size: 3em;
                margin-bottom: 15px;
            }}
            
            @media (max-width: 600px) {{
                .container {{
                    border-radius: 0;
                }}
                
                h1 {{
                    font-size: 1.8em;
                }}
                
                .form-row {{
                    flex-direction: column;
                }}
                
                .task-item {{
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 10px;
                }}
                
                .task-amount {{
                    align-self: flex-end;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Task Manager</h1>
            </div>
            
            <div class="total-section">
                <div class="total-label">Running Total</div>
                <div class="total-amount" id="runningTotal">₹{running_total:.2f}</div>
            </div>
            
            <div class="add-task-section">
                <form id="taskForm">
                    <div class="form-row">
                        <input type="text" id="taskName" placeholder="Task name" required>
                        <input type="number" id="taskAmount" placeholder="Amount" step="0.01" required>
                    </div>
                    <button type="submit" class="add-btn">Add Task</button>
                </form>
            </div>
            
            <div class="tasks-section" id="tasksList">
                {tasks_html if tasks_html else '<div class="empty-state"><div class="empty-state-icon">📋</div><div>No tasks yet</div></div>'}
            </div>
        </div>
        
        <script>
            // Add new task
            document.getElementById('taskForm').addEventListener('submit', async (e) => {{
                e.preventDefault();
                const taskName = document.getElementById('taskName').value;
                const taskAmount = parseFloat(document.getElementById('taskAmount').value);
                
                const response = await fetch('/api/tasks', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{task_name: taskName, amount: taskAmount}})
                }});
                
                if (response.ok) {{
                    location.reload();
                }}
            }});
            
            // Toggle task completion
            document.querySelectorAll('.task-checkbox').forEach(checkbox => {{
                checkbox.addEventListener('change', async (e) => {{
                    const taskId = e.target.dataset.id;
                    const response = await fetch(`/api/tasks/${{taskId}}/toggle`, {{
                        method: 'PUT'
                    }});
                    
                    if (response.ok) {{
                        location.reload();
                    }}
                }});
            }});
            
            // Delete task
            document.querySelectorAll('.delete-btn').forEach(button => {{
                button.addEventListener('click', async (e) => {{
                    const taskId = e.target.dataset.id;
                    if (confirm('Are you sure you want to delete this task?')) {{
                        const response = await fetch(`/api/tasks/${{taskId}}`, {{
                            method: 'DELETE'
                        }});
                        
                        if (response.ok) {{
                            location.reload();
                        }}
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """

# Routes
@app.get("/", response_class=HTMLResponse)
def home():
    return render_page()

@app.post("/api/tasks")
async def create_task(task_data: TaskCreate):
    """Create a new task and save to TodoTasks.json"""
    with file_lock:
        todo_tasks = load_json_file(TODO_FILE)
        
        # Get all tasks to determine next ID
        all_tasks = todo_tasks + load_json_file(DONE_FILE)
        new_id = get_next_id(all_tasks)
        
        new_task = {
            "id": new_id,
            "task_name": task_data.task_name,
            "amount": task_data.amount,
            "created_at": datetime.now().isoformat(),
            "date": get_today_date()
        }
        
        todo_tasks.append(new_task)
        save_json_file(TODO_FILE, todo_tasks)
        
        return {"id": new_id, "task_name": task_data.task_name, "amount": task_data.amount}

@app.get("/api/tasks")
def get_tasks():
    """Get all tasks for today"""
    with file_lock:
        todo_tasks = load_json_file(TODO_FILE)
        done_tasks = load_json_file(DONE_FILE)
    
    today = get_today_date()
    # today_tasks = [t for t in todo_tasks if t['date'] == today]
    done_task_ids = {t['id'] for t in done_tasks}
    
    result = []
    for task in todo_tasks:
        is_done = task['id'] in done_task_ids
        completed_at = None
        if is_done:
            done_task = next((t for t in done_tasks if t['id'] == task['id']), None)
            if done_task:
                completed_at = done_task['completed_at']
        
        result.append({
            "id": task['id'],
            "task_name": task['task_name'],
            "amount": task['amount'],
            "is_done": is_done,
            "created_at": task['created_at'],
            "completed_at": completed_at
        })
    
    return result

@app.put("/api/tasks/{task_id}/toggle")
def toggle_task(task_id: int):
    """Toggle task completion status"""
    with file_lock:
        todo_tasks = load_json_file(TODO_FILE)
        done_tasks = load_json_file(DONE_FILE)
        
        # Find the task in todo list
        task = next((t for t in todo_tasks if t['id'] == task_id), None)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Check if already done
        is_done = any(t['id'] == task_id for t in done_tasks)
        
        if is_done:
            # Remove from done list (uncomplete)
            done_tasks = [t for t in done_tasks if t['id'] != task_id]
            save_json_file(DONE_FILE, done_tasks)
            return {"id": task_id, "is_done": False}
        else:
            # Add to done list
            done_task = {
                "id": task['id'],
                "task_name": task['task_name'],
                "amount": task['amount'],
                "created_at": task['created_at'],
                "completed_at": datetime.now().isoformat(),
                "date": task['date'],
                "printed": False
            }
            done_tasks.append(done_task)
            save_json_file(DONE_FILE, done_tasks)
            return {"id": task_id, "is_done": True}

@app.get("/api/total")
def get_total():
    """Get running total"""
    total = get_running_total()
    return {"running_total": total}

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    """Delete a task completely from both JSON files"""
    with file_lock:
        todo_tasks = load_json_file(TODO_FILE)
        done_tasks = load_json_file(DONE_FILE)
        
        # Find and remove from todo list
        todo_tasks = [t for t in todo_tasks if t['id'] != task_id]
        
        # Find and remove from done list
        done_tasks = [t for t in done_tasks if t['id'] != task_id]
        
        save_json_file(TODO_FILE, todo_tasks)
        save_json_file(DONE_FILE, done_tasks)
        
        return {"success": True, "message": "Task deleted"}

@app.get("/next_task")
def get_next_task():
    """Get latest unprinted completed task and mark it as printed"""
    with file_lock:
        done_tasks = load_json_file(DONE_FILE)
        
        if not done_tasks:
            return {}
        
        # Filter unprinted tasks (tasks without 'printed' field or with printed=False)
        unprinted_tasks = [t for t in done_tasks if not t.get('printed', False)]
        
        if not unprinted_tasks:
            return {}
        
        # Get latest unprinted task by completed_at timestamp
        latest_task = max(unprinted_tasks, key=lambda x: x['completed_at'])
        
        # Mark as printed
        for task in done_tasks:
            if task['id'] == latest_task['id']:
                task['printed'] = True
                break
        
        save_json_file(DONE_FILE, done_tasks)
        
        return {
            "task": latest_task['task_name'],
            "amount": str(latest_task['amount']),
            "completed_at": latest_task['completed_at']
        }

