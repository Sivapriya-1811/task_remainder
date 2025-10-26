import streamlit as st
import pandas as pd
from datetime import datetime, date
from plyer import notification
import time

# --- Helper Functions ---
def load_tasks():
    try:
        return pd.read_csv("tasks.csv").to_dict('records')
    except FileNotFoundError:
        return []

def save_tasks(tasks):
    df = pd.DataFrame(tasks)
    df.to_csv("tasks.csv", index=False)

def send_desktop_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=8  # seconds
    )

# --- Streamlit App UI ---
st.set_page_config(page_title="Task Reminder Dashboard", layout="centered")
st.title("📝 Task Reminder Dashboard")

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

# --- Reminder Checking Function ---
def check_and_alert():
    today = date.today()
    overdue_tasks = []
    due_today_tasks = []

    for task in st.session_state.tasks:
        due = pd.to_datetime(task["Due Date"]).date()
        if task["Status"] == "Pending":
            if due < today:
                overdue_tasks.append(task["Task"])
            elif due == today:
                due_today_tasks.append(task["Task"])

    if overdue_tasks:
        msg = f"Overdue Tasks: {', '.join(overdue_tasks)}"
        st.error(f"⚠️ {msg}")
        send_desktop_notification("⚠️ Task Reminder Alert", msg)
    elif due_today_tasks:
        msg = f"Tasks Due Today: {', '.join(due_today_tasks)}"
        st.warning(f"📅 {msg}")
        send_desktop_notification("📅 Task Reminder Alert", msg)
    else:
        st.success("✅ No pending tasks due now!")

# --- Add Task Form ---
st.subheader("➕ Add a New Task")
task_name = st.text_input("Task Name")
task_desc = st.text_area("Task Description")
due_date = st.date_input("Due Date")
priority = st.selectbox("Priority", ["Low", "Medium", "High"])

if st.button("Add Task"):
    new_task = {
        "Task": task_name,
        "Description": task_desc,
        "Due Date": due_date,
        "Priority": priority,
        "Status": "Pending"
    }
    st.session_state.tasks.append(new_task)
    save_tasks(st.session_state.tasks)
    st.success(f"✅ Task '{task_name}' added successfully!")

# --- Display Tasks ---
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    st.subheader("📋 Task List")
    st.dataframe(df)

    # --- Mark Task as Completed ---
    pending_tasks = [t["Task"] for t in st.session_state.tasks if t["Status"] == "Pending"]
    if pending_tasks:
        completed_task = st.selectbox("Mark a task as completed", ["Select"] + pending_tasks)
        if st.button("✅ Mark Completed"):
            for task in st.session_state.tasks:
                if task["Task"] == completed_task:
                    task["Status"] = "Completed"
                    st.success(f"🎯 Task '{completed_task}' marked as completed!")
                    save_tasks(st.session_state.tasks)
                    break
    else:
        st.info("All tasks are completed! 🎉")

else:
    st.info("No tasks yet. Add a task to get started!")

# --- Auto Reminder Loop ---
st.divider()
st.subheader("🔔 Auto Reminder Settings")
interval = st.number_input("Check interval (in minutes):", min_value=1, max_value=120, value=1)

if st.button("▶️ Start Auto Reminders"):
    st.info(f"Auto reminders running every {interval} minute(s)...")
    while True:
        check_and_alert()
        time.sleep(interval * 60)
