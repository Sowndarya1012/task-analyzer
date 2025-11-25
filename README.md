Task Priority Analyzer

A Django-based backend and HTML/CSS/JS frontend application designed to analyze, rank, and suggest high-priority tasks based on urgency, importance, effort, and dependencies. 


Overview
The Task Priority Analyzer is a smart productivity tool that ranks tasks using a weighted scoring algorithm. The goal is to help users decide what they should work on right now, given multiple factors such as urgency, importance, effort, and dependencies.

Features
Backend
- Django + Django REST Framework API
- Priority scoring engine
- Strategy-based ranking
- Task validation
- Dependency-aware scoring
- Suggests top 3 tasks
- Unit-tested scoring logic

Frontend
- Clean, responsive UI
- Add tasks manually
- Bulk JSON input
- Sorting strategy dropdown
- Color-coded results
- Error handling + validation

Tech Stack
Backend: Python, Django, DRF
Frontend: HTML, CSS, JavaScript
Database: SQLite

Setup Instructions

1.Clone the repository

git clone https://github.com/<your-username>/task-analyzer.git
cd task-analyzer

2.Set up the backend environment

python -m venv venv

For windows

venv\Scripts\activate

For Mac/Linux

source venv/bin/activate


3.Install dependencies

pip install -r requirements.txt

4.Run migrations

cd backend
python manage.py migrate

5.Start the server.

python manage.py runserver

6.Set up the frontend using a simple HTTP server.

API Documentation

POST /api/tasks/analyze/
GET /api/tasks/suggest/

Algorithm Explanation

The Task Priority Analyzer uses a weighted scoring algorithm that evaluates each task based on four main components: urgency, importance, effort, and dependencies. The goal of the algorithm is to emulate how humans naturally decide which tasks are worth prioritizing, while providing a quantifiable and explainable output.

Urgency is determined by comparing the task’s due date with the current date. Tasks due very soon receive a high urgency score. Tasks that are overdue receive an even higher score because they require immediate attention. Tasks due far in the future receive lower urgency values. This ensures the system respects deadlines realistically.

Importance is based directly on the user’s 1–10 rating. This allows subjective judgment—sometimes a task is not urgent but is strategically important. The importance score is normalized to a 0–1 scale to match urgency scoring and combined accordingly.

Effort (estimated hours) contributes to the "quick win" philosophy. Tasks requiring fewer hours receive better scores because they can be completed faster and create momentum. This helps users clear small tasks early and reduces cognitive load. High-effort tasks reduce the overall score slightly, encouraging a balance between major and minor tasks.

Dependencies add a multiplier effect. A task that blocks other tasks becomes more critical, as completing it unlocks progress. A task with many dependencies gets a boost in priority score.

All these components are then combined into a final weighted score. The Smart Balance strategy uses a balanced weighting across all components. Other strategies modify weights:

Fastest Wins → gives higher weight to low effort.

High Impact → importance dominates.

Deadline Driven → urgency dominates.

This makes the algorithm configurable based on user preference.

The final score is used to sort tasks from highest to lowest priority. The returned result includes a detailed explanation of why the score was assigned, making the system transparent and easy to understand.

Design Decisions

-Django REST Framework was chosen for clean serialization, API routing, and validation.

-Vanilla JavaScript was used to keep the frontend lightweight.

-Separate frontend & backend allows independent deployment and testing.

-JSON input was chosen instead of database to simplify submission.

-Score explanation was added to improve transparency.

-Strategy selection allows users to choose based on their work style.

Time Breakdown
Backend setup: 30 min
Algorithm: 45 min
API: 45 min
Frontend: 1 hr
Testing: 30 min
Docs: 20 min

Future Improvements
- Add authentication
- Add analytics dashboard
- Save tasks to database
- Drag & drop UI

