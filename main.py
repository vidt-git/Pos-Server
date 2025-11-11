# server.py
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()
pending_job = None
last_submitted = None


def render_form(message: str = ""):
    """Reusable HTML form with inline CSS for mobile responsiveness"""
    return f"""
    <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                }}
                .container {{
                    max-width: 400px;
                    margin: auto;
                    background: #fff;
                    padding: 25px;
                    border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                h2 {{
                    color: #333;
                }}
                input {{
                    width: 90%;
                    padding: 10px;
                    margin: 8px 0;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    font-size: 16px;
                }}
                button {{
                    width: 95%;
                    padding: 10px;
                    background: #007bff;
                    border: none;
                    color: white;
                    font-size: 16px;
                    border-radius: 5px;
                    cursor: pointer;
                }}
                button:hover {{
                    background: #0056b3;
                }}
                .message {{
                    margin-bottom: 10px;
                    color: green;
                    font-weight: bold;
                }}
                @media (max-width: 600px) {{
                    .container {{
                        width: 95%;
                        padding: 15px;
                    }}
                    input, button {{
                        font-size: 15px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>POS Print Form</h2>
                {f"<div class='message'>{message}</div>" if message else ""}
                <form method="post">
                    <input type="text" name="task" placeholder="Task" required><br>
                    <input type="text" name="amount" placeholder="Amount / Number" required><br>
                    <button type="submit">Print</button>
                </form>
            </div>
        </body>
    </html>
    """


@app.get("/", response_class=HTMLResponse)
def home():
    return render_form(f"Last sent: {last_submitted}" if last_submitted else "")


@app.post("/", response_class=HTMLResponse)
def submit_form(task: str = Form(...), amount: str = Form(...)):
    global pending_job, last_submitted
    pending_job = {"task": task, "amount": amount}
    last_submitted = f"{task} - {amount}"
    return render_form(f"✅ Sent to printer: {task} - {amount}")


@app.get("/next_job")
def get_next_job():
    global pending_job
    job = pending_job
    pending_job = None
    return job or {}



