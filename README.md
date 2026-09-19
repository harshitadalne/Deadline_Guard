# 🛡️ Deadline Guardian

### Real-Time Intelligent Deadline Management & Recommendation System

Deadline Guardian is a web-based productivity application designed to help students manage multiple academic, professional, and personal deadlines.

Instead of simply storing tasks like a traditional to-do application, Deadline Guardian analyzes **deadline urgency, task importance, estimated effort, and available time** to determine what the user should focus on next.

The system uses a **Priority Queue and deterministic scheduling algorithms** for core task prioritization, while an **LLM** is used for natural-language task creation, task understanding, and personalized recommendations.

---

## 🎯 Problem Statement

Students often manage multiple assignments, examinations, projects, coding tests, interviews, applications, and other activities simultaneously.

Traditional task-management applications mainly show tasks and deadlines but do not answer questions such as:

* What should I work on first?
* Which deadline is at risk?
* Can I finish everything before the deadline?
* Do I have enough time for all my pending tasks?
* What should I work on right now?

**Deadline Guardian** aims to solve these problems through intelligent, real-time task prioritization and personalized recommendations.

---

## 💡 Key Idea

The application follows a simple principle:

> **Algorithms decide the priority.
> Real-time data updates the priority.
> LLM understands and explains the results.**

The LLM is **not** responsible for basic priority calculations. Deterministic algorithms handle scheduling and prioritization, making the system transparent and explainable.

---

## ✨ Planned Features

### 📋 Task Management

* Create tasks
* Edit tasks
* Delete tasks
* Mark tasks as completed
* Start/Pause tasks
* Set deadlines
* Set estimated duration
* Set importance and difficulty
* Categorize tasks

### 🧠 Intelligent Prioritization

Tasks are prioritized using:

* Deadline urgency
* Importance
* Estimated effort
* Time remaining
* Workload pressure

A **Priority Queue** is used to efficiently retrieve the highest-priority task.

### 🚨 Deadline Risk Detection

Tasks are classified into:

* 🟢 Low
* 🟡 Medium
* 🟠 High
* 🔴 Critical

The system detects when the estimated work is greater than the available time.

### ⏱️ Workload Analysis

The application compares:

```text
Available Time
        vs
Required Work
```

and detects workload conflicts.

### 📅 Smart Scheduling

The system generates a daily schedule based on:

* Current time
* Task priority
* Deadlines
* Estimated duration
* Available time

### 🤖 LLM / NLP Features

The LLM will be used for:

* Natural-language task creation
* Natural-language queries
* Personalized recommendations
* Task decomposition
* Human-readable explanations

Example:

> "I have a DBMS assignment tomorrow which will take 3 hours."

The system can extract the task details and allow the user to confirm them before saving.

### 💬 Ask Guardian

Users can ask:

> "What should I do now?"

> "Which tasks are at risk?"

> "Can I finish everything today?"

> "Give me a plan for tomorrow."

The system first analyzes actual task data and then uses the LLM to generate a natural-language response.

### 🔔 Notifications

The application will provide alerts for:

* Upcoming deadlines
* High-risk tasks
* Critical tasks
* Overdue tasks

### 📊 Productivity Analytics

Planned analytics include:

* Task completion rate
* Overdue tasks
* Estimated vs actual time
* Category-wise productivity
* Weekly productivity

---

# 🏗️ System Architecture

```text
                       USER
                         │
                         ▼
                ┌─────────────────┐
                │    Streamlit    │
                │    Frontend     │
                └────────┬────────┘
                         │
                         │ HTTP
                         ▼
                ┌─────────────────┐
                │     FastAPI     │
                │     Backend     │
                └────────┬────────┘
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
        ┌─────────┐ ┌──────────┐ ┌─────────┐
        │ SQLite  │ │ Priority │ │   LLM   │
        │Database │ │  Engine  │ │  Layer  │
        └─────────┘ └────┬─────┘ └─────────┘
                         │
                    ┌────▼────┐
                    │ Priority│
                    │  Queue  │
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │  Risk & │
                    │ Workload│
                    │ Analysis │
                    └────┬────┘
                         │
                         ▼
                  Recommendation
```

---

# 🧮 Priority Calculation

The core priority score will be calculated using deterministic logic.

The current planned formula is:

```text
Priority Score =
    0.50 × Urgency
  + 0.30 × Importance
  + 0.20 × Effort Pressure
```

Where:

### Urgency

Determined by the amount of time remaining until the deadline.

### Importance

Based on:

```text
Low
Medium
High
Critical
```

### Effort Pressure

Represents how much of the remaining available time is required to complete the task.

The resulting score is used by the **Priority Queue**.

---

# 🧱 Technology Stack

### Frontend

* Python
* Streamlit
* Plotly

### Backend

* Python
* FastAPI
* Uvicorn

### Database

* SQLite
* SQLAlchemy

### Algorithms

* Priority Queue
* Heap
* Greedy Scheduling
* Deadline Scheduling
* Time-based calculations

### AI / NLP

* LLM API
* Natural Language Processing

### Testing

* Pytest
* FastAPI TestClient

---

# 📁 Project Structure

The project is being developed incrementally.

```text
deadline_guardian/
│
├── backend/
│   ├── __init__.py
│   └── main.py
│
├── frontend/
│   └── app.py
│
├── tests/
│   └── test_setup.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

The structure will expand as additional modules are implemented.

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone <repository-url>
cd deadline_guardian
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Start the FastAPI backend

```bash
uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## 5. Start the Streamlit frontend

Open another terminal and activate the virtual environment.

Then:

```bash
streamlit run frontend/app.py
```

Frontend:

```text
http://localhost:8501
```

---

# 🧪 Running Tests

Run:

```bash
pytest
```

Current Phase 1 tests verify:

* FastAPI root endpoint
* Health-check endpoint

Expected result:

```text
2 passed
```

As development progresses, tests will be added for:

* Database operations
* Task CRUD
* Priority calculation
* Priority Queue
* Risk detection
* Workload analysis
* Scheduling
* APIs
* LLM response validation
* End-to-end workflows

---

# 🗺️ Development Roadmap

The project is being developed phase by phase.

* [x] Phase 0 — Requirements & Architecture
* [x] Phase 1 — Project Setup
* [ ] Phase 2 — Database & SQLAlchemy Models
* [ ] Phase 3 — Task CRUD
* [ ] Phase 4 — Priority Engine
* [ ] Phase 5 — Priority Queue
* [ ] Phase 6 — Risk & Workload Engine
* [ ] Phase 7 — Scheduling Engine
* [ ] Phase 8 — FastAPI Backend
* [ ] Phase 9 — Streamlit Frontend
* [ ] Phase 10 — Frontend & Backend Integration
* [ ] Phase 11 — Real-Time Updates
* [ ] Phase 12 — LLM/NLP Integration
* [ ] Phase 13 — Notifications
* [ ] Phase 14 — Analytics
* [ ] Phase 15 — Authentication & Security
* [ ] Phase 16 — End-to-End Testing
* [ ] Phase 17 — Deployment

---

# 🔐 Security

The project will follow basic security practices:

* Password hashing
* Environment variables for API keys
* No hardcoded secrets
* Input validation
* User authorization
* SQLAlchemy ORM for database operations
* Validation of LLM-generated structured data

Sensitive configuration will be stored in `.env`.

Example:

```text
LLM_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///./deadline_guardian.db
```

The `.env` file should **never be committed to GitHub**.

---

# 🔮 Future Scope

Future versions may include:

* 📅 Google Calendar integration
* 📱 Mobile application
* 🎙️ Voice-based task creation
* 🧠 ML-based deadline prediction
* 📈 Personalized productivity modeling
* ☁️ Cloud database
* 🔔 Push notifications
* 🤖 Advanced AI productivity assistant

---

# 👩‍💻 Development Philosophy

Deadline Guardian follows a **hybrid intelligent-system approach**.

Instead of using AI for everything:

```text
                    Deadline Guardian
                           │
             ┌─────────────┴─────────────┐
             │                           │
       Deterministic                   LLM
         Engine                       Layer
             │                           │
       Priority Queue                  NLP
       Risk Analysis            Task Understanding
       Scheduling                Recommendations
       Workload Analysis          Explanations
             │                           │
             └─────────────┬─────────────┘
                           │
                           ▼
                  Intelligent Assistant
```

This makes the system:

* Explainable
* Efficient
* Testable
* Reliable
* Practical

---

# 📌 Current Status

**Development Phase: Phase 1 — Project Setup**

Current functionality:

* FastAPI backend
* Streamlit frontend
* Health-check endpoint
* Automated tests
* Project structure
* Development environment

The application is being developed incrementally with automated testing at every major phase.

---

## 👤 Author

**Sakhi**

B.Tech — Artificial Intelligence & Data Science

---

## ⭐ Project Vision

> **Don't just track deadlines. Know what to do next.**

---
