# Halleyx Workflow Engine

A full-stack workflow automation system built with **Python FastAPI** backend and a **professional HTML/JS** frontend with 4 switchable themes.

---

## Features

- Design workflows with multiple steps (Task, Approval, Notification)
- Define conditional rules with a powerful rule engine (`&&`, `||`, `==`, `contains()`, `DEFAULT`, etc.)
- Execute workflows with dynamic input data
- Track every step with detailed execution logs
- 4 professional themes: Dark, Light, Midnight, Rose
- Full audit log of all executions
- Interactive rule editor with priority ordering

---

## Project Structure

```
halleyx_workflow/
├── index.html          ← Frontend UI (open in browser)
├── requirements.txt    ← Python dependencies
├── README.md
└── app/
    ├── __init__.py
    ├── database.py     ← SQLite connection setup
    ├── models.py       ← Database tables (Workflow, Step, Rule, Execution)
    ├── schemas.py      ← Request/Response validation (Pydantic)
    ├── rule_engine.py  ← Condition evaluator engine
    └── main.py         ← FastAPI app with all 16 API routes
```

---

## Setup & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the backend server

```bash
cd halleyx_workflow
python -m uvicorn app.main:app --reload
```

Server runs at: `http://127.0.0.1:8000`  
API docs at: `http://127.0.0.1:8000/docs`

### 3. Open the frontend

Open `index.html` directly in your browser (double-click or drag into browser).

---

## API Endpoints

### Workflows
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workflows` | Create workflow |
| GET | `/workflows` | List workflows (search, pagination) |
| GET | `/workflows/:id` | Get workflow details |
| PUT | `/workflows/:id` | Update workflow (auto-increments version) |
| DELETE | `/workflows/:id` | Delete workflow |

### Steps
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workflows/:id/steps` | Add step |
| GET | `/workflows/:id/steps` | List steps |
| PUT | `/steps/:id` | Update step |
| DELETE | `/steps/:id` | Delete step |

### Rules
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/steps/:id/rules` | Add rule |
| GET | `/steps/:id/rules` | List rules |
| PUT | `/rules/:id` | Update rule |
| DELETE | `/rules/:id` | Delete rule |

### Execution
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workflows/:id/execute` | Start execution |
| GET | `/executions` | List all executions (audit log) |
| GET | `/executions/:id` | Get execution detail + logs |
| POST | `/executions/:id/cancel` | Cancel execution |
| POST | `/executions/:id/retry` | Retry failed execution |

---

## Rule Engine

Conditions support:
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `&&` (AND), `||` (OR)
- String: `contains(field, "value")`, `startsWith(field, "prefix")`, `endsWith(field, "suffix")`
- Fallback: `DEFAULT` — always matches, use as last rule

**Example Rules for "Manager Approval" step:**
| Priority | Condition | Next Step |
|----------|-----------|-----------|
| 1 | `amount > 100 && country == "US" && priority == "High"` | Finance Notification |
| 2 | `amount <= 100` | CEO Approval |
| 3 | `priority == "Low"` | Task Rejection |
| 4 | `DEFAULT` | Task Rejection |

---

## Sample Workflow: Expense Approval

**Input Schema:**
```json
{
  "amount": {"type": "number", "required": true},
  "country": {"type": "string", "required": true},
  "priority": {"type": "string", "required": true, "allowed_values": ["High", "Medium", "Low"]}
}
```

**Steps:**
1. Manager Approval (approval)
2. Finance Notification (notification)
3. CEO Approval (approval)
4. Task Rejection (task)

**Execution Example Input:**
```json
{"amount": 250, "country": "US", "priority": "High"}
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, FastAPI |
| Database | SQLite + SQLAlchemy ORM |
| Validation | Pydantic v2 |
| Server | Uvicorn (ASGI) |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Fonts | Syne + JetBrains Mono |

---

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Halleyx Workflow Engine"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/halleyx-workflow.git
git push -u origin main
```

---

## Deploy to Render (Free)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set these values:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 10000`
5. Deploy — your API will be live at `https://your-app.onrender.com`
6. Update `const API = '...'` in `index.html` to point to your Render URL

---

*Built for Halleyx Full Stack Engineer Challenge 2026*
