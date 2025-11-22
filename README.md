# Café Todo - Coffee Shop Todo List App

A beautiful, coffee-themed todo list application with database persistence, running totals, and automatic end-of-day processing.

## Features

- ☕ **Coffee Shop Aesthetic**: Warm brown tones and cozy design
- 📝 **Task Management**: Add tasks with amounts, toggle completion status
- 💰 **Running Total**: Automatically calculates total from completed tasks
- ⏰ **End-of-Day Processing**: Automatically deducts 50% of unfinished tasks at 11:59 PM
- 🏠 **Home Server Integration**: `/next_job` endpoint for external polling
- 📱 **Mobile Responsive**: Works great on all devices
- 💾 **Persistent Storage**: SQLite database keeps your data safe

## Setup

### Local Development

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Open in browser**:
   Navigate to `http://localhost:8000`

## API Endpoints

### Web Interface
- `GET /` - Main todo list interface

### API Endpoints
- `POST /api/tasks` - Create a new task
  - Body: `{"task_name": "Task name", "amount": 10.50}`
- `GET /api/tasks` - Get all tasks
- `PUT /api/tasks/{id}/toggle` - Toggle task completion status
- `GET /api/total` - Get current running total

### Home Server Integration
- `GET /next_job` - Get next uncompleted task for processing
  - Returns: `{"task": "task name", "amount": "10.50"}` or `{}`
- `POST /complete_job` - Mark a task as complete
  - Form data: `task_name=<task name>`

## Deployment on Render

### Option 1: Deploy with SQLite (Free Tier)

1. **Create a new Web Service** on [Render](https://render.com)

2. **Connect your GitHub repository**

3. **Configure the service**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3

4. **Add Environment Variable** (optional):
   - Key: `DATABASE_URL`
   - Value: `sqlite:///./todos.db`

5. **Deploy!**

### Option 2: Deploy with PostgreSQL (Recommended for Production)

1. **Create a PostgreSQL database** on Render

2. **Update the Web Service**:
   - Add the PostgreSQL database as an environment variable
   - Render will automatically set `DATABASE_URL`

3. **Update requirements.txt** to include PostgreSQL driver:
   ```
   psycopg2-binary==2.9.9
   ```

4. **Redeploy**

### Important Notes for Render

- **Persistence**: SQLite data will be lost when the service restarts on free tier. Use PostgreSQL for production.
- **Disk Storage**: Render free tier has ephemeral storage - database will reset on each deployment.
- **Scheduled Tasks**: The end-of-day processing runs at 11:59 PM server time (UTC).

## How It Works

### Task Lifecycle

1. **Add Task**: User creates a task with a name and amount
2. **Process Task**: Task appears in the list, home server can poll `/next_job` to get it
3. **Complete Task**: Either toggle checkbox in UI or call `/complete_job` from home server
4. **Running Total**: Completed task amounts are added to running total
5. **End of Day**: At 11:59 PM, unfinished tasks trigger 50% deduction from running total

### Database Schema

**Tasks Table**:
- `id`: Primary key
- `task_name`: Task description
- `amount`: Task amount/value
- `is_done`: Completion status
- `created_at`: Creation timestamp
- `completed_at`: Completion timestamp

**DailyTotals Table**:
- `id`: Primary key
- `date`: Record date
- `deduction_amount`: Amount deducted
- `notes`: Reason for deduction

**PendingTasks Table**:
- `id`: Primary key
- `task_id`: Reference to task
- `sent_at`: When task was sent to home server

## Customization

### Change End-of-Day Time

Edit the scheduler configuration in `main.py`:
```python
scheduler.add_job(process_end_of_day, CronTrigger(hour=23, minute=59))
```

### Adjust Deduction Percentage

Edit the `process_end_of_day()` function:
```python
deduction = sum(task.amount * 0.5 for task in unfinished_tasks)  # Change 0.5 to your percentage
```

### Customize Colors

Modify the CSS in the `render_page()` function to change the coffee shop theme colors.

## Troubleshooting

### Database Issues
- Delete `todos.db` file and restart to reset the database
- Check file permissions if SQLite fails to write

### Scheduler Not Running
- Verify APScheduler is installed: `pip show apscheduler`
- Check server logs for scheduler errors

### Home Server Can't Connect
- Ensure firewall allows incoming connections
- Verify the correct URL/port is being used
- Check that `/next_job` endpoint returns expected format

## License

MIT License - Feel free to use and modify!

## Support

For issues or questions, please open an issue on GitHub.

---

Made with ☕ and ❤️
