[![Unit](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/python-app.yml)
[![API (in-memory)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/api-inmemory.yml/badge.svg?branch=main)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/api-inmemory.yml)
[![API (Mongo)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/api-mongo.yml/badge.svg?branch=main)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/api-mongo.yml)
[![BDD (in-memory)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/bdd-inmemory.yml/badge.svg?branch=main)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/bdd-inmemory.yml)
[![BDD (Mongo)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/bdd-mongo.yml/badge.svg?branch=main)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/bdd-mongo.yml)
[![Perf (in-memory)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/perf-inmemory.yml/badge.svg?branch=main)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/perf-inmemory.yml)
[![Perf (Mongo)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/perf-mongo.yml/badge.svg?branch=main)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/perf-mongo.yml)
[![UI (in-memory)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/ui-inmemory.yml/badge.svg?branch=main)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/ui-inmemory.yml)
[![UI (Mongo)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/ui-mongo.yml/badge.svg?branch=main)](https://github.com/Vera-Kibin/task-manager-2025/actions/workflows/ui-mongo.yml)

# Task Manager 2025

Task Manager 2025 is a backend-driven task management application built with Flask and React. It features a clean separation of domain logic, repository interfaces, and integrations. The project supports both in-memory and MongoDB backends, and includes comprehensive tests (unit, API, BDD, performance, and UI).

---

## Features

- Create tasks with field validation (`title`, `priority`).
- Assign tasks with role-based permissions (`owner`/`manager`).
- Update task fields (`title`, `description`, `priority`) with validation.
- Transition task statuses (`NEW -> IN_PROGRESS -> DONE/CANCELED`).
- Soft delete tasks (`is_deleted=True`) with idempotency.
- List tasks with filters (`status`, `priority`) and role-based visibility.
- View task history (`CREATED`, `ASSIGNED`, `STATUS_CHANGED`, `UPDATED`, `DELETED`).
- Send task history via email (mocked SMTP in tests).

---

## Demo

1. **Registration**  
   <video src="https://github.com/user-attachments/assets/e805b91e-3623-4e15-a546-fed638d3b4aa" width="900" controls muted playsinline></video>

2. **Create Task**  
   <video src="https://github.com/user-attachments/assets/b57303aa-541a-402c-aac5-666ab84581f3" width="900" controls muted playsinline></video>

3. **Edit Task**  
   <video src="https://github.com/user-attachments/assets/6d0189a1-ef2e-4d35-9ce6-8ca4b45d5665" width="900" controls muted playsinline></video>

4. **Status Flow & Filters**  
   <video src="https://github.com/user-attachments/assets/3a6cdded-6d82-4bb0-88c2-5f57ebacfd0e" width="900" controls muted playsinline></video>

---

### Prerequisites

- Python 3.10+
- Node.js 20+ and npm
- Docker (only for MongoDB or running CI locally)

## Quickstart

### Backend (In-memory)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export PYTHONPATH=$PWD
python3 -m flask --app app.api:create_app run  # http://127.0.0.1:5000
```

### Backend (MongoDB)

```bash
docker compose -f mongo.yml up -d
export STORAGE=mongo
export MONGO_URI="mongodb://localhost:27017"
export MONGO_DB="taskmgr"

export PYTHONPATH=$PWD
python3 -m flask --app app.api:create_app run  # http://127.0.0.1:5000
```

### Frontend (Vite)

```bash
cd web && npm ci

# In-memory
npm run dev -- --host 127.0.0.1 --port 5173

# Mongo
VITE_API_URL=http://127.0.0.1:5000 npm run dev -- --host 127.0.0.1 --port 5173

# App URL
http://127.0.0.1:5173
```

---

## Tests

### Unit

```bash
python3 -m pytest tests/unit -q
python3 -m coverage run --source=src -m pytest tests/unit
python3 -m coverage report -m
```

### API (Black-box)

```bash
python3 -m pytest tests/api -q
```

### BDD (Behave)

```bash
python3 -m behave tests/bdd -q
```

### Performance

```bash
python3 -m pytest tests/perf -q
```

### UI Tests (Playwright)

```bash
cd web && npm ci && npx playwright install
npx playwright test
npx playwright show-report
```

---

## CI

The project includes GitHub Actions workflows for testing and CI/CD:

- `python-app.yml` — Unit tests + coverage.
- `api-inmemory.yml` / `api-mongo.yml` — API tests.
- `bdd-inmemory.yml` / `bdd-mongo.yml` — BDD scenarios.
- `perf-inmemory.yml` / `perf-mongo.yml` — Performance tests.
- `ui-inmemory.yml` / `ui-mongo.yml` — Playwright UI tests.

---

## Tech Stack

- **Backend:** Flask (Python 3.10+)
- **Database:** MongoDB (prod), in-memory (test)
- **Frontend:** React + TypeScript + Vite
  - **Forms & Validation:** Formik, Yup
  - **Styling:** Tailwind CSS
- **Testing:** Pytest, Behave, Playwright
- **CI/CD:** GitHub Actions

---

## Future Work

- Extend `User` model with first/last name.
- Implement real SMTP for email notifications.
- Add WebSocket updates for real-time task changes.
- Introduce dark mode for the frontend.
- Support task tags and attachments.

## License & Attribution

- Code: [MIT](./LICENSE)
- UI demo assets: short screen recordings by the author.
- Cat GIF/video credit: source link https://i.gifer.com/Xjgr.gif (used for illustrative purposes).

From NEW to DONE — one paw at a time. 🐾
