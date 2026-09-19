import streamlit as st
import requests
from datetime import datetime, timezone, timedelta
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="Deadline Guardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def api_request(method, endpoint, data=None, token=None):
    """Make API request to backend."""
    url = f"{BACKEND_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=5)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=5)
        
        if response.status_code in [200, 201]:  # Handle both 200 OK and 201 Created
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    .greeting {
        font-size: 1.2rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    .priority-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .summary-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1e3a8a;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)


def check_backend_connection():
    """Check if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def login_page():
    """Display login page."""
    st.title("🛡️ Deadline Guardian")
    st.subheader("Login to continue")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Make API login request
        login_data = {"email": email, "password": password}
        result = api_request("POST", "/auth/login", login_data)
        
        if result:
            st.session_state.logged_in = True
            st.session_state.token = result["access_token"]
            st.session_state.user_email = email
            st.success("Login successful!")
            st.rerun()
    
    if st.button("Register"):
        st.session_state.show_register = True
        st.rerun()


def register_page():
    """Display registration page."""
    st.title("🛡️ Deadline Guardian")
    st.subheader("Create an account")
    
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match")
        else:
            # Make API registration request
            register_data = {"name": name, "email": email, "password": password}
            result = api_request("POST", "/auth/register", register_data)
            
            if result:
                st.success("Registration successful! Please login.")
                st.session_state.show_register = False
                st.rerun()
    
    if st.button("Back to Login"):
        st.session_state.show_register = False
        st.rerun()


def main():
    """Main application."""
    # Check backend connection
    if not check_backend_connection():
        st.warning("⚠️ Backend server is not running. Please start the backend with: uvicorn backend.main:app --reload")
    
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "show_register" not in st.session_state:
        st.session_state.show_register = False
    
    # Show login/register page if not logged in
    if not st.session_state.logged_in:
        if st.session_state.show_register:
            register_page()
        else:
            login_page()
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🛡️ Deadline Guardian")
        st.write(f"Good {get_time_greeting()}, {st.session_state.user_email} 👋")
        
        page = st.radio(
            "Navigation",
            [
                "🏠 Dashboard",
                "📋 My Tasks",
                "📅 Schedule",
                "🤖 Ask Guardian",
                "📊 Analytics",
                "🔔 Notifications",
                "⚙️ Settings"
            ]
        )
        
        st.divider()
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.user_email = None
            st.rerun()
    
    # Display selected page
    if page == "🏠 Dashboard":
        dashboard_page()
    elif page == "📋 My Tasks":
        tasks_page()
    elif page == "📅 Schedule":
        schedule_page()
    elif page == "🤖 Ask Guardian":
        guardian_page()
    elif page == "📊 Analytics":
        analytics_page()
    elif page == "🔔 Notifications":
        notifications_page()
    elif page == "⚙️ Settings":
        settings_page()


def get_time_greeting():
    """Get appropriate greeting based on time of day."""
    hour = datetime.now().hour
    if hour < 12:
        return "morning"
    elif hour < 17:
        return "afternoon"
    else:
        return "evening"


def dashboard_page():
    """Display dashboard page."""
    st.markdown('<div class="main-header">🛡️ Deadline Guardian</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="greeting">Good {get_time_greeting()}, {st.session_state.user_email} 👋</div>', unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add Task", use_container_width=True):
            st.session_state.show_add_task = True
    with col2:
        if st.button("🤖 Ask Guardian", use_container_width=True):
            st.session_state.page = "🤖 Ask Guardian"
            st.rerun()
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            # Force refresh priorities
            api_request("GET", "/dashboard/refresh", token=st.session_state.token)
            st.rerun()
    
    st.divider()
    
    # Fetch dashboard data from API
    summary = api_request("GET", "/dashboard/summary", token=st.session_state.token)
    priority_rec = api_request("GET", "/dashboard/priority", token=st.session_state.token)
    schedule = api_request("GET", "/dashboard/schedule/today", token=st.session_state.token)
    
    if summary:
        # Summary cards
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.markdown(f"""
            <div class="summary-card">
                <div class="metric-value">{summary['total_tasks']}</div>
                <div class="metric-label">Total Tasks</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="summary-card">
                <div class="metric-value">{summary['pending']}</div>
                <div class="metric-label">Pending</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="summary-card">
                <div class="metric-value">{summary['completed']}</div>
                <div class="metric-label">Completed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="summary-card">
                <div class="metric-value">{summary['overdue']}</div>
                <div class="metric-label">Overdue</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="summary-card">
                <div class="metric-value">{summary['critical']}</div>
                <div class="metric-label">Critical</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="summary-card">
                <div class="metric-value">{summary['high_risk']}</div>
                <div class="metric-label">High Risk</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Today's Priority
    st.subheader("🔥 YOUR NEXT TASK")
    
    if priority_rec and priority_rec.get("next_task"):
        task = priority_rec["next_task"]
        risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}.get(task["risk_level"], "⚪")
        
        deadline_str = datetime.fromisoformat(task["deadline"]).strftime("%B %d, %I:%M %p")
        
        st.markdown(f"""
        <div class="priority-card">
            <h2>{task['title']}</h2>
            <p><strong>Priority:</strong> {task['priority_score']:.1f}/100</p>
            <p><strong>Risk:</strong> {risk_emoji} {task['risk_level']}</p>
            <p><strong>Deadline:</strong> {deadline_str}</p>
            <p><strong>Estimated Work:</strong> {task['estimated_hours']} hours</p>
            <p><strong>Importance:</strong> {task['importance']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("▶ Start Task", use_container_width=True, key="start_next_task"):
            # Start the task
            api_request("POST", f"/tasks/{task['id']}/start", token=st.session_state.token)
            st.success("Task started!")
            st.rerun()
    else:
        st.info("No pending tasks. You're all caught up! 🎉")
    
    st.divider()
    
    # Today's Schedule
    st.subheader("📅 Today's Schedule")
    
    if schedule and schedule.get("tasks"):
        for task in schedule["tasks"]:
            st.markdown(f"**{task['start_time']} – {task['end_time']}** – {task['title']}")
    else:
        st.info("No tasks scheduled for today.")


def tasks_page():
    """Display tasks page."""
    st.title("📋 My Tasks")
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Add Task", use_container_width=True):
            st.session_state.show_add_task = True
    with col2:
        if st.button("🤖 AI Add Task", use_container_width=True):
            st.session_state.show_ai_add_task = True
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col4:
        if st.button("🗑️ Clear Completed", use_container_width=True):
            st.info("Clear completed tasks feature coming soon")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Completed", "Overdue"])
    with col2:
        category_filter = st.selectbox("Filter by Category", ["All", "Academic", "Project", "DSA", "Interview", "Application", "Personal", "Event", "Other"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Deadline", "Priority", "Importance"])
    
    # Fetch tasks
    tasks = api_request("GET", "/tasks/", token=st.session_state.token)
    
    if tasks:
        # Apply filters
        if status_filter != "All":
            tasks = [t for t in tasks if t["status"] == status_filter]
        if category_filter != "All":
            tasks = [t for t in tasks if t["category"] == category_filter]
        
        # Apply sorting
        if sort_by == "Deadline":
            tasks.sort(key=lambda t: t["deadline"])
        elif sort_by == "Priority":
            tasks.sort(key=lambda t: t["priority_score"], reverse=True)
        elif sort_by == "Importance":
            importance_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
            tasks.sort(key=lambda t: importance_order.get(t["importance"], 4))
        
        # Display tasks
        for task in tasks:
            with st.expander(f"{task['title']} - {task['status']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Category:** {task['category']}")
                    st.write(f"**Deadline:** {datetime.fromisoformat(task['deadline']).strftime('%B %d, %I:%M %p')}")
                    st.write(f"**Estimated:** {task['estimated_duration_minutes']} minutes")
                    st.write(f"**Importance:** {task['importance']}")
                    st.write(f"**Difficulty:** {task['difficulty']}")
                    st.write(f"**Priority:** {task['priority_score']:.1f}/100")
                    st.write(f"**Risk:** {task['risk_level']}")
                    if task['description']:
                        st.write(f"**Description:** {task['description']}")
                
                with col2:
                    if task['status'] == "Pending":
                        if st.button("▶ Start", key=f"start_{task['id']}"):
                            api_request("POST", f"/tasks/{task['id']}/start", token=st.session_state.token)
                            st.rerun()
                    elif task['status'] == "In Progress":
                        if st.button("⏸ Pause", key=f"pause_{task['id']}"):
                            api_request("POST", f"/tasks/{task['id']}/pause", token=st.session_state.token)
                            st.rerun()
                        if st.button("✓ Complete", key=f"complete_{task['id']}"):
                            api_request("POST", f"/tasks/{task['id']}/complete", token=st.session_state.token)
                            st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"delete_{task['id']}"):
                        api_request("DELETE", f"/tasks/{task['id']}", token=st.session_state.token)
                        st.rerun()
    else:
        st.info("No tasks found.")
    
    # Add task modal
    if st.session_state.get("show_add_task", False):
        st.subheader("➕ Add New Task")
        
        with st.form("add_task_form"):
            title = st.text_input("Title*")
            description = st.text_area("Description")
            category = st.selectbox("Category*", ["Academic", "Project", "DSA", "Interview", "Application", "Personal", "Event", "Other"])
            deadline = st.datetime_input("Deadline*")
            estimated_duration = st.number_input("Estimated Duration (minutes)*", min_value=1, value=60)
            importance = st.selectbox("Importance*", ["Low", "Medium", "High", "Critical"])
            difficulty = st.selectbox("Difficulty*", ["Easy", "Medium", "Hard"])
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Add Task")
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            if submit:
                task_data = {
                    "title": title,
                    "description": description,
                    "category": category,
                    "deadline": deadline.isoformat(),
                    "estimated_duration_minutes": estimated_duration,
                    "importance": importance,
                    "difficulty": difficulty
                }
                result = api_request("POST", "/tasks/", task_data, token=st.session_state.token)
                if result:
                    st.success("Task added successfully!")
                    st.session_state.show_add_task = False
                    st.rerun()
            
            if cancel:
                st.session_state.show_add_task = False
                st.rerun()
    
    # AI task creation modal
    if st.session_state.get("show_ai_add_task", False):
        st.subheader("🤖 Add Task with AI")
        
        natural_input = st.text_area(
            "Describe your task in natural language...",
            placeholder="Example: I need to complete my DBMS assignment tomorrow evening. It will take about 3 hours and it is very important.",
            height=100
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🤖 Parse Task"):
                if natural_input:
                    parse_data = {"natural_language": natural_input, "user_id": 1}
                    result = api_request("POST", "/guardian/parse-task", parse_data, token=st.session_state.token)
                    
                    if result:
                        parsed_task = result.get("parsed_task", {})
                        st.success("Task parsed successfully!")
                        
                        # Display parsed data for confirmation
                        st.write(f"**Title:** {parsed_task.get('title', 'N/A')}")
                        st.write(f"**Deadline:** {parsed_task.get('deadline', 'N/A')}")
                        st.write(f"**Duration:** {parsed_task.get('estimated_duration_minutes', 'N/A')} minutes")
                        st.write(f"**Importance:** {parsed_task.get('importance', 'N/A')}")
                        st.write(f"**Category:** {parsed_task.get('category', 'N/A')}")
                        
                        # Store parsed task for confirmation
                        st.session_state.parsed_task = parsed_task
                    else:
                        st.error("Failed to parse task. AI features may be unavailable.")
                else:
                    st.warning("Please enter a task description.")
        
        with col2:
            if st.button("✓ Create Task"):
                if st.session_state.get("parsed_task"):
                    parsed = st.session_state.parsed_task
                    
                    # Convert deadline string to datetime
                    try:
                        deadline_dt = datetime.fromisoformat(parsed['deadline'])
                    except:
                        deadline_dt = datetime.now(timezone.utc) + timedelta(days=1)
                    
                    task_data = {
                        "title": parsed['title'],
                        "description": parsed.get('description', ''),
                        "category": parsed['category'],
                        "deadline": deadline_dt.isoformat(),
                        "estimated_duration_minutes": parsed['estimated_duration_minutes'],
                        "importance": parsed['importance'],
                        "difficulty": "Medium"  # Default difficulty
                    }
                    
                    result = api_request("POST", "/tasks/", task_data, token=st.session_state.token)
                    
                    if result:
                        st.success("Task created successfully!")
                        st.session_state.parsed_task = None
                        st.session_state.show_ai_add_task = False
                        st.rerun()
                    else:
                        st.error("Failed to create task.")
                else:
                    st.warning("Please parse a task first.")
        
        with col3:
            if st.button("Cancel"):
                st.session_state.parsed_task = None
                st.session_state.show_ai_add_task = False
                st.rerun()


def schedule_page():
    """Display schedule page."""
    st.title("📅 Schedule")
    
    col1, col2 = st.columns(2)
    with col1:
        available_hours = st.number_input("Available Hours Today", min_value=1, max_value=24, value=8)
    with col2:
        if st.button("Generate Schedule"):
            st.rerun()
    
    # Get today's schedule
    schedule = api_request("GET", f"/dashboard/schedule/today?available_hours={available_hours}", token=st.session_state.token)
    
    if schedule:
        st.subheader(f"Today's Schedule - {schedule['date']}")
        st.write(f"Available: {schedule['available_hours']} hours | Scheduled: {schedule['scheduled_hours']} hours | Remaining: {schedule['remaining_hours']} hours")
        
        if schedule['tasks']:
            for task in schedule['tasks']:
                st.markdown(f"**{task['start_time']} – {task['end_time']}** – {task['title']} ({task['duration_hours']}h)")
        else:
            st.info("No tasks scheduled for today.")
    
    st.divider()
    
    # Get weekly schedule
    weekly = api_request("GET", "/dashboard/schedule/weekly", token=st.session_state.token)
    
    if weekly and weekly.get("weekly_schedule"):
        st.subheader("📅 Weekly Schedule")
        
        for day_schedule in weekly["weekly_schedule"]:
            with st.expander(f"{day_schedule['date']} - {day_schedule['used_hours']}/{day_schedule['available_hours']} hours"):
                if day_schedule['tasks']:
                    for task in day_schedule['tasks']:
                        st.markdown(f"• {task['title']} ({task['estimated_hours']}h) - {task['importance']}")
                else:
                    st.write("No tasks scheduled.")


def guardian_page():
    """Display guardian chat page."""
    st.title("🤖 Ask Deadline Guardian")
    
    # Tab navigation for different Guardian features
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "➕ AI Task Creation", "🎯 Recommendations"])
    
    with tab1:
        st.subheader("Chat with Deadline Guardian")
        st.write("Ask questions about your tasks, deadlines, and schedule.")
        
        # Chat interface
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
        
        # Chat input
        user_input = st.chat_input("Ask Deadline Guardian...")
        
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Get AI response
            chat_data = {"message": user_input, "user_id": 1}  # user_id would come from auth
            response = api_request("POST", "/guardian/chat", chat_data, token=st.session_state.token)
            
            if response:
                ai_response = response.get("response", "I couldn't process that request.")
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                st.rerun()
            else:
                st.error("Failed to get response from Guardian. AI features may be unavailable.")
    
    with tab2:
        st.subheader("Add Task with AI")
        st.write("Describe your task in natural language and let AI extract the details.")
        
        natural_input = st.text_area(
            "Describe your task...",
            placeholder="Example: I need to complete my DBMS assignment tomorrow evening. It will take about 3 hours and it is very important.",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 Parse Task"):
                if natural_input:
                    parse_data = {"natural_language": natural_input, "user_id": 1}
                    result = api_request("POST", "/guardian/parse-task", parse_data, token=st.session_state.token)
                    
                    if result:
                        parsed_task = result.get("parsed_task", {})
                        st.success("Task parsed successfully!")
                        
                        # Display parsed data for confirmation
                        st.subheader("📋 Parsed Task Details")
                        st.write(f"**Title:** {parsed_task.get('title', 'N/A')}")
                        st.write(f"**Deadline:** {parsed_task.get('deadline', 'N/A')}")
                        st.write(f"**Duration:** {parsed_task.get('estimated_duration_minutes', 'N/A')} minutes")
                        st.write(f"**Importance:** {parsed_task.get('importance', 'N/A')}")
                        st.write(f"**Category:** {parsed_task.get('category', 'N/A')}")
                        if parsed_task.get('description'):
                            st.write(f"**Description:** {parsed_task['description']}")
                        
                        # Store parsed task for confirmation
                        st.session_state.parsed_task = parsed_task
                    else:
                        st.error("Failed to parse task. AI features may be unavailable.")
                else:
                    st.warning("Please enter a task description.")
        
        with col2:
            if st.button("Clear"):
                st.session_state.parsed_task = None
                st.rerun()
        
        # Show confirmation if task was parsed
        if st.session_state.get("parsed_task"):
            st.divider()
            st.subheader("Confirm and Create Task")
            
            if st.button("✓ Create Task"):
                parsed = st.session_state.parsed_task
                
                # Convert deadline string to datetime
                try:
                    deadline_dt = datetime.fromisoformat(parsed['deadline'])
                except:
                    deadline_dt = datetime.now(timezone.utc) + timedelta(days=1)
                
                task_data = {
                    "title": parsed['title'],
                    "description": parsed.get('description', ''),
                    "category": parsed['category'],
                    "deadline": deadline_dt.isoformat(),
                    "estimated_duration_minutes": parsed['estimated_duration_minutes'],
                    "importance": parsed['importance'],
                    "difficulty": "Medium"  # Default difficulty
                }
                
                result = api_request("POST", "/tasks/", task_data, token=st.session_state.token)
                
                if result:
                    st.success("Task created successfully!")
                    st.session_state.parsed_task = None
                    st.rerun()
                else:
                    st.error("Failed to create task.")
    
    with tab3:
        st.subheader("AI-Powered Recommendations")
        
        # Get AI recommendation
        rec_data = {"user_id": 1, "available_hours": 8.0}
        recommendation = api_request("POST", "/guardian/recommendation", rec_data, token=st.session_state.token)
        
        if recommendation:
            st.write("**Recommendation:**")
            st.write(recommendation.get("explanation", "No recommendation available."))
            
            if recommendation.get("next_task"):
                task = recommendation["next_task"]
                st.divider()
                st.subheader("🎯 Next Task to Work On")
                st.write(f"**{task['title']}**")
                st.write(f"Priority: {task['priority_score']:.1f}/100 | Risk: {task['risk_level']}")
                st.write(f"Deadline: {datetime.fromisoformat(task['deadline']).strftime('%B %d, %I:%M %p')}")
                st.write(f"Estimated: {task['estimated_hours']} hours")
        else:
            st.info("Recommendations are currently unavailable.")


def analytics_page():
    """Display analytics page."""
    st.title("📊 Productivity Analytics")
    
    # Get tasks
    tasks = api_request("GET", "/tasks/", token=st.session_state.token)
    
    if tasks:
        # Basic statistics
        total = len(tasks)
        completed = len([t for t in tasks if t['status'] == 'Completed'])
        pending = len([t for t in tasks if t['status'] in ['Pending', 'In Progress']])
        overdue = len([t for t in tasks if t['deadline'] < datetime.now(timezone.utc).isoformat() and t['status'] != 'Completed'])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tasks", total)
        with col2:
            st.metric("Completed", completed)
        with col3:
            st.metric("Pending", pending)
        with col4:
            st.metric("Overdue", overdue)
        
        st.divider()
        
        # Tasks by category - Pie chart
        st.subheader("Tasks by Category")
        categories = {}
        for task in tasks:
            cat = task['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        if categories:
            df = pd.DataFrame(list(categories.items()), columns=['Category', 'Count'])
            fig = px.pie(df, values='Count', names='Category', title='Tasks by Category')
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Tasks by importance - Bar chart
        st.subheader("Tasks by Importance")
        importance = {}
        for task in tasks:
            imp = task['importance']
            importance[imp] = importance.get(imp, 0) + 1
        
        if importance:
            df = pd.DataFrame(list(importance.items()), columns=['Importance', 'Count'])
            fig = px.bar(df, x='Importance', y='Count', title='Tasks by Importance', color='Importance')
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Tasks by risk level - Bar chart
        st.subheader("Tasks by Risk Level")
        risk_levels = {}
        for task in tasks:
            risk = task['risk_level']
            risk_levels[risk] = risk_levels.get(risk, 0) + 1
        
        if risk_levels:
            df = pd.DataFrame(list(risk_levels.items()), columns=['Risk Level', 'Count'])
            color_map = {'LOW': 'green', 'MEDIUM': 'yellow', 'HIGH': 'orange', 'CRITICAL': 'red'}
            fig = px.bar(df, x='Risk Level', y='Count', title='Tasks by Risk Level', 
                        color='Risk Level', color_discrete_map=color_map)
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Priority distribution - Histogram
        st.subheader("Priority Score Distribution")
        priority_scores = [t['priority_score'] for t in tasks]
        if priority_scores:
            fig = px.histogram(x=priority_scores, nbins=20, title='Priority Score Distribution',
                            labels={'x': 'Priority Score', 'y': 'Count'})
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Task status breakdown
        st.subheader("Task Status Breakdown")
        status_counts = {}
        for task in tasks:
            status = task['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            df = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
            fig = px.pie(df, values='Count', names='Status', title='Task Status Breakdown')
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Completion rate
        if total > 0:
            completion_rate = (completed / total) * 100
            st.subheader("Completion Rate")
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = completion_rate,
                title = {'text': "Completion Rate (%)"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 25], 'color': "lightgray"},
                        {'range': [25, 50], 'color': "gray"},
                        {'range': [50, 75], 'color': "lightblue"},
                        {'range': [75, 100], 'color': "blue"}
                    ],
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No tasks found for analytics.")


def notifications_page():
    """Display notifications page."""
    st.title("🔔 Notifications")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh Notifications"):
            api_request("POST", "/notifications/generate", token=st.session_state.token)
            st.rerun()
    with col2:
        if st.button("✓ Mark All as Read"):
            api_request("POST", "/notifications/read-all", token=st.session_state.token)
            st.rerun()
    
    # Generate notifications
    api_request("POST", "/notifications/generate", token=st.session_state.token)
    
    # Get notifications
    notifications = api_request("GET", "/notifications/?unread_only=true", token=st.session_state.token)
    
    if notifications:
        st.subheader(f"📬 {len(notifications)} Unread Notifications")
        
        for notification in notifications:
            with st.container():
                if notification['notification_type'] == 'overdue':
                    st.error(notification['message'])
                elif notification['notification_type'] in ['risk_critical', 'deadline_soon']:
                    st.warning(notification['message'])
                else:
                    st.info(notification['message'])
                
                created_time = datetime.fromisoformat(notification['created_at']).strftime("%B %d, %I:%M %p")
                st.caption(f"📅 {created_time}")
                
                if st.button("✓ Mark as Read", key=f"read_{notification['id']}"):
                    api_request("POST", f"/notifications/{notification['id']}/read", token=st.session_state.token)
                    st.rerun()
                
                st.divider()
    else:
        st.success("✅ No unread notifications!")
    
    st.divider()
    
    # Show tasks that need attention as fallback
    st.subheader("⚠️ Tasks Needing Attention")
    tasks = api_request("GET", "/tasks/", token=st.session_state.token)
    
    if tasks:
        # Filter for tasks that need attention
        attention_tasks = [
            t for t in tasks 
            if t['risk_level'] in ['HIGH', 'CRITICAL'] or 
               (t['deadline'] < datetime.now(timezone.utc).isoformat() and t['status'] != 'Completed')
        ]
        
        if attention_tasks:
            for task in attention_tasks:
                risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}.get(task["risk_level"], "⚪")
                deadline_str = datetime.fromisoformat(task["deadline"]).strftime("%B %d, %I:%M %p")
                
                if task['deadline'] < datetime.now(timezone.utc).isoformat():
                    st.error(f"🚨 OVERDUE: {task['title']} was due on {deadline_str}")
                else:
                    st.warning(f"{risk_emoji} {task['risk_level']}: {task['title']} due {deadline_str}")
        else:
            st.info("No tasks need immediate attention.")


def settings_page():
    """Display settings page."""
    st.title("⚙️ Settings")
    
    st.subheader("Application Settings")
    
    # Backend URL
    backend_url = st.text_input("Backend URL", value=os.getenv("BACKEND_URL", "http://localhost:8000"))
    
    # Auto-refresh settings
    auto_refresh = st.checkbox("Auto-refresh dashboard", value=True)
    refresh_interval = st.slider("Refresh interval (seconds)", min_value=10, max_value=300, value=60)
    
    if st.button("Save Settings"):
        st.success("Settings saved!")
        st.info("Some settings may require restarting the application.")
    
    st.divider()
    
    st.subheader("Account Information")
    st.write(f"**Email:** {st.session_state.user_email}")
    
    st.divider()
    
    st.subheader("About")
    st.write("**Deadline Guardian v1.0.0**")
    st.write("Real-Time Intelligent Deadline Management & Recommendation System")
    st.write("Built with FastAPI, Streamlit, and Python")


if __name__ == "__main__":
    main()
