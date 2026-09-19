# 🛡️ Deadline Guardian

Real-Time Intelligent Deadline Management & Recommendation System

A production-quality web application designed primarily for college students who have multiple assignments, exams, projects, coding tests, interviews, applications, and personal deadlines.

## 🎯 Core Principle

**Algorithms decide task priority. Real-time data keeps priorities updated. An LLM understands natural language and explains/recommends what the user should do.**

The system uses deterministic algorithms and a Priority Queue for priority calculations, NOT AI/LLM. The LLM is only used for natural language understanding and explaining algorithmic results.

## ✨ Features

### User Management
- ✅ User registration and login
- ✅ Secure password hashing with bcrypt
- ✅ JWT-based authentication
- ✅ Session management

### Task Management
- ✅ Create, edit, delete tasks
- ✅ Mark tasks as completed
- ✅ Start/pause task tracking
- ✅ Filter, search, and sort tasks
- ✅ Task categories: Academic, Project, DSA, Interview, Application, Personal, Event, Other
- ✅ Importance levels: Low, Medium, High, Critical
- ✅ Difficulty levels: Easy, Medium, Hard

### Intelligent Priority System
- ✅ **Priority Engine**: Calculates priority scores based on:
  - Deadline urgency (closer deadline = higher urgency)
  - Task importance (Critical > High > Medium > Low)
  - Effort pressure (estimated work vs available time)
- ✅ **Priority Queue**: Uses Python's `heapq` for efficient task ordering
- ✅ **Dynamic Priority**: Priorities update automatically as time passes
- ✅ **Risk Engine**: Calculates risk levels (LOW, MEDIUM, HIGH, CRITICAL)
- ✅ **Workload Detection**: Identifies when workload exceeds available time

### Dashboard
- ✅ Real-time summary cards (Total, Pending, Completed, Overdue, Critical, High Risk)
- ✅ Today's priority task with detailed explanation
- ✅ Today's schedule with time slots
- ✅ Auto-refresh functionality

### AI/NLP Integration
- ✅ Natural language task creation ("I need to complete my DBMS assignment tomorrow evening...")
- ✅ AI-powered task decomposition
- ✅ Chat interface for asking questions about tasks
- ✅ Human-readable explanations of algorithmic recommendations

### Notifications
- ✅ In-app deadline notifications
- ✅ Risk-based alerts (HIGH, CRITICAL)
- ✅ Overdue task warnings
- ✅ Deadline approaching reminders

### Analytics
- ✅ Completion rate visualization
- ✅ Tasks by category (pie chart)
- ✅ Tasks by importance (bar chart)
- ✅ Tasks by risk level (bar chart)
- ✅ Priority score distribution (histogram)
- ✅ Task status breakdown

## 🏗️ Architecture

### Technology Stack

**Frontend:**
- Streamlit (Python web framework)
- Plotly (interactive charts)
- Custom CSS for styling

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy ORM
- SQLite database
- Python `heapq` for priority queue
- OpenAI API for LLM integration

**Key Algorithms:**
- Priority Queue (heapq-based)
- Greedy scheduling
- Deadline calculations
- Workload conflict detection

### Project Structure

```
deadline_guardian/
│
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API endpoints
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── tasks.py           # Task CRUD endpoints
│   │   ├── dashboard.py       # Dashboard endpoints
│   │   ├── guardian.py        # AI/LLM endpoints
│   │   └── notifications.py   # Notification endpoints
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── base.py            # Base model
│   │   ├── user.py            # User model
│   │   ├── task.py            # Task model
│   │   ├── timelog.py         # Time tracking model
│   │   └── notification.py    # Notification model
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py            # User schemas
│   │   ├── task.py            # Task schemas
│   │   └── guardian.py        # Guardian/AI schemas
│   │
│   ├── services/               # Business logic
│   │   ├── priority_constants.py  # Configuration constants
│   │   ├── priority_engine.py     # Priority calculation
│   │   ├── priority_queue.py      # Priority queue implementation
│   │   ├── risk_engine.py         # Risk calculation
│   │   ├── workload_engine.py      # Workload analysis
│   │   ├── scheduler.py            # Task scheduling
│   │   ├── notification_service.py # Notification generation
│   │   ├── llm_service.py          # LLM integration
│   │   └── auth_service.py         # Authentication logic
│   │
│   ├── database/               # Database configuration
│   │   ├── database.py        # Database setup
│   │   └── seed.py            # Demo data seeding
│   │
│   └── config.py               # Application configuration
│
├── frontend/
│   ├── app.py                  # Streamlit application
│   ├── pages/                  # Page components
│   ├── components/             # Reusable components
│   └── styles/                 # Custom CSS
│
├── tests/                      # Unit tests
│   ├── test_priority_engine.py
│   ├── test_risk_engine.py
│   ├── test_workload_engine.py
│   └── test_priority_queue.py
│
├── .env.example               # Environment variables template
├── requirements.txt            # Python dependencies
├── README.md                  # This file
└── run.py                     # Application runner
```

## 🧮 Priority Calculation

### Formula

```
priority_score = 0.50 * urgency + 0.30 * importance + 0.20 * effort_pressure
```

### Components

**1. Urgency Score (0-100)**
- ≤ 2 hours: 100
- ≤ 6 hours: 90
- ≤ 12 hours: 80
- ≤ 24 hours: 70
- ≤ 3 days: 50
- ≤ 7 days: 30
- > 7 days: 10

**2. Importance Score (0-100)**
- Critical: 100
- High: 75
- Medium: 50
- Low: 25

**3. Effort Pressure (0-100)**
- Calculated as: `estimated_duration / available_time_until_deadline * 100`
- Normalized to 0-100 scale

### Example

A task due in 4 hours (urgency: 90), with High importance (75), requiring 2 hours of work with 4 hours available (pressure: 50):

```
priority_score = 0.50 * 90 + 0.30 * 75 + 0.20 * 50
             = 45 + 22.5 + 10
             = 77.5
```

## 🚨 Risk Levels

**LOW**: Work is ≤ 50% of available time
- 🟢 Safe to schedule later

**MEDIUM**: Work is ≤ 80% of available time
- 🟡 Should start soon

**HIGH**: Work is ≤ 100% of available time
- 🟠 Time is limited, start now

**CRITICAL**: Work exceeds available time
- 🔴 Immediate action required

## 🤖 LLM Integration

The LLM (OpenAI GPT) is responsible for:

1. **Natural Language Processing**
   - Understanding task descriptions
   - Extracting structured task information
   - Parsing deadlines and durations

2. **Explanation Generation**
   - Explaining algorithmic recommendations
   - Creating human-readable plans
   - Answering natural language questions

3. **Task Decomposition**
   - Breaking complex tasks into subtasks
   - Suggesting task breakdowns

**Important**: The LLM NEVER:
- Calculates priority scores
- Decides deadlines
- Modifies database records without confirmation
- Overrides the Priority Queue
- Marks tasks as completed

The deterministic algorithms remain the source of truth.

## 📊 Database Schema

### Users Table
- `id` (Primary Key)
- `name`
- `email` (Unique)
- `password_hash`
- `created_at`

### Tasks Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `title`
- `description`
- `category`
- `deadline`
- `estimated_duration_minutes`
- `importance`
- `difficulty`
- `status`
- `priority_score`
- `risk_level`
- `created_at`
- `updated_at`
- `started_at`
- `completed_at`

### TimeLogs Table
- `id` (Primary Key)
- `task_id` (Foreign Key)
- `start_time`
- `end_time`
- `duration_minutes`

### Notifications Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `task_id` (Foreign Key)
- `message`
- `notification_type`
- `is_read`
- `created_at`

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user
- `GET /auth/me` - Get current user info

### Tasks
- `GET /tasks/` - Get all tasks
- `POST /tasks/` - Create new task
- `GET /tasks/{id}` - Get specific task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task
- `POST /tasks/{id}/complete` - Mark task as completed
- `POST /tasks/{id}/start` - Start task
- `POST /tasks/{id}/pause` - Pause task

### Dashboard
- `GET /dashboard/summary` - Get dashboard statistics
- `GET /dashboard/priority` - Get priority recommendation
- `GET /dashboard/schedule/today` - Get today's schedule
- `GET /dashboard/schedule/weekly` - Get weekly schedule
- `GET /dashboard/workload` - Get workload analysis
- `GET /dashboard/refresh` - Refresh dashboard data

### Guardian (AI)
- `POST /guardian/parse-task` - Parse task from natural language
- `POST /guardian/recommendation` - Get AI-powered recommendation
- `POST /guardian/chat` - Chat with AI assistant
- `POST /guardian/decompose-task` - Decompose task into subtasks

### Notifications
- `GET /notifications/` - Get notifications
- `POST /notifications/generate` - Generate new notifications
- `POST /notifications/{id}/read` - Mark notification as read
- `POST /notifications/read-all` - Mark all as read
- `DELETE /notifications/old` - Delete old notifications

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd DeadLine-Guard
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and set your configuration:
```env
DATABASE_URL=sqlite:///./deadline_guardian.db
SECRET_KEY=your-secret-key-here
LLM_API_KEY=your-openai-api-key-here  # Optional - AI features will work without this
LLM_MODEL=gpt-3.5-turbo
BACKEND_URL=http://localhost:8000
```

**Note**: The `.env` file is in `.gitignore` to protect sensitive data. Create it manually from `.env.example`.

5. **Initialize database with demo data**
```bash
python run.py seed
```

## 🏃 Running the Application

### Option 1: Using the run script

**Start Backend:**
```bash
python run.py backend
```

**Start Frontend:**
```bash
python run.py frontend
```

### Option 2: Manual startup

**Start Backend (in one terminal):**
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Start Frontend (in another terminal):**
```bash
cd frontend
streamlit run app.py --server.port 8501
```

### Access the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Demo User

The seed script creates a demo user:
- **Email**: demo@student.edu
- **Password**: demo123

## 🧪 Testing

Run the unit tests:

```bash
pytest tests/ -v
```

Run specific test files:

```bash
pytest tests/test_priority_engine.py -v
pytest tests/test_risk_engine.py -v
pytest tests/test_workload_engine.py -v
pytest tests/test_priority_queue.py -v
```

## 🔒 Security

- ✅ Passwords hashed with bcrypt
- ✅ JWT-based authentication
- ✅ SQL injection protection via SQLAlchemy
- ✅ Input validation with Pydantic
- ✅ Environment variables for sensitive data
- ✅ No hardcoded API keys
- ✅ Validation of LLM-generated data

## 📈 Future Enhancements

### Planned Features
- [ ] Mobile app development
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Email notifications
- [ ] Team collaboration features
- [ ] Advanced analytics with ML predictions
- [ ] Pomodoro timer integration
- [ ] Subtask management
- [ ] Task dependencies
- [ ] Recurring tasks
- [ ] Tags and labels

### ML Extension
The database is designed to support future ML features:
- Historical productivity data collection
- Task completion prediction models
- Personalized priority weight optimization
- Estimated duration accuracy improvement

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with FastAPI and Streamlit
- Priority queue implementation using Python's heapq
- LLM integration with OpenAI API
- Charts powered by Plotly

## 📞 Support

For issues, questions, or suggestions, please open an issue on the repository.

---

**Built with ❤️ for students who need to manage their deadlines intelligently**
#   D e a d l i n e _ G u a r d  
 #   D e a d l i n e _ G u a r d  
 #   D e a d l i n e _ G u a r d  
 