from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Pydantic models
class TaskCreate(BaseModel):
    task_name: str
    amount: float
    time_from: Optional[str] = None
    time_to: Optional[str] = None

class Task(BaseModel):
    id: int
    task_name: str
    amount: float
    created_at: str
    date: str  # Date in YYYY-MM-DD format for filtering
    time_from: Optional[str] = None
    time_to: Optional[str] = None

class DoneTask(BaseModel):
    id: int
    task_name: str
    amount: float
    created_at: str
    completed_at: str
    date: str
    time_from: Optional[str] = None
    time_to: Optional[str] = None

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

def get_render_data():
    """Get data for rendering the page"""
    with file_lock:
        todo_tasks = load_json_file(TODO_FILE)
        done_tasks = load_json_file(DONE_FILE)
        running_total = sum(task['amount'] for task in done_tasks)
    
    today = get_today_date()
    
    # Filter tasks for today
    today_tasks = [t for t in todo_tasks if t['date'] == today]
    
    # Create a set of done task IDs for quick lookup
    done_task_ids = {t['id'] for t in done_tasks}
    
    # Regular tasks list
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
    
    # Timebox tasks (sorted by time)
    timed_tasks = [t for t in today_tasks if t.get('time_from')]
    timed_tasks.sort(key=lambda x: x.get('time_from', ''))
    
    timebox_html = ""
    for task in timed_tasks:
        is_done = task['id'] in done_task_ids
        task_class = "done" if is_done else ""
        time_range = f"{task.get('time_from', '')} - {task.get('time_to', '')}"
        
        timebox_html += f"""
        <div class="timebox-item {task_class}">
            <div class="timebox-time">{time_range}</div>
            <div class="timebox-task-name">{task['task_name']}</div>
            <div class="timebox-amount">₹{task['amount']:.2f}</div>
            <div class="timebox-actions">
                <input type="checkbox" class="task-checkbox" data-id="{task['id']}" {'checked' if is_done else ''}>
                <button class="delete-btn-small" data-id="{task['id']}">🗑️</button>
            </div>
        </div>
        """
    
    # Calculate progress
    total_count = len(today_tasks)
    completed_count = sum(1 for t in today_tasks if t['id'] in done_task_ids)
    
    return {
        "tasks_html": tasks_html,
        "timebox_html": timebox_html,
        "running_total": running_total,
        "completed_count": completed_count,
        "total_count": total_count
    }

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = get_render_data()
    return templates.TemplateResponse("index.html", {
        "request": request,
        **data
    })

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
        
        if task_data.time_from:
            new_task["time_from"] = task_data.time_from
        if task_data.time_to:
            new_task["time_to"] = task_data.time_to
        
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
            if task.get('time_from'):
                done_task['time_from'] = task['time_from']
            if task.get('time_to'):
                done_task['time_to'] = task['time_to']
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

