# server.py
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()
pending_job = None

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <form method='post'>
        Task: <input name='task'><br>
        Number: <input name='number'><br>
        <button type='submit'>Print</button>
    </form>
    """

@app.post("/")
def submit_form(task: str = Form(...), number: str = Form(...)):
    global pending_job
    pending_job = {"task": task, "number": number}
    return {"message": "Sent to printer!"}

@app.get("/next_job")
def get_next_job():
    global pending_job
    job = pending_job
    pending_job = None
    return job or {}

