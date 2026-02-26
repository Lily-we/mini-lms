# Mini LMS (MVP)

A small LMS-like website built for a thesis/dissertation defense MVP.

It supports:
- Login-required access
- 4–5 Sections (Bo‘limlar)
- Materials inside each section:
  - Text
  - Links
  - YouTube videos (with fallback link)
  - Drawings/files (PDF/PNG preview + download)
  - DXF download
  - Telegram private channel links
  - Quizzes (results visible only after submission)

---

## Tech Stack
- Django 5.x
- SQLite (local dev)
- Django Admin for content management

---

## Features (MVP)
### Student side
- Login to access content
- Browse sections and materials
- Take quizzes and submit answers
- Quiz results are shown only after submission
- View attempt history (`/my-attempts/`) (if enabled)

### Admin side
- Manage Sections / Content Items / File Assets in Django Admin
- Create quizzes: Quiz → Questions → Choices

---

## Local Setup (Windows + Git Bash)
### 1) Create virtualenv & install requirements
```bash
py -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt