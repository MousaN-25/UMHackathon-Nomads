# BizMind — AI Business Advisor

An AI-powered full-stack web app for young entrepreneurs.

---

## Project Structure

```
BizMind/
├── backend/
│   └── main.py          ← FastAPI server + GLM integration
├── frontend/
│   └── index.html       ← Single-file frontend (HTML + CSS + JS)
├── data/
│   └── businesses.json  ← Local database for smart matching
├── requirements.txt
└── README.md
```

---

## Setup & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your GLM API key

Open `backend/main.py` and find these two lines near the top:

```python
GLM_API_URL = "YOUR_API_URL"
GLM_API_KEY = "YOUR_API_KEY"
```

Replace them with your actual GLM API credentials.

### 3. Start the backend

```bash
cd backend
uvicorn main:app --reload
```

The backend runs at: http://localhost:8000

### 4. Open the frontend

Just open `frontend/index.html` in your browser (double-click or drag into Chrome).

---

## How to Demo

1. Go to the **Advisor** tab
2. Describe your business and enter weekday/weekend sales
3. Click **Analyze My Business**
4. See AI-generated Insight, Recommendation, and Explanation
5. Switch to the **Chat** tab and ask follow-up questions
6. Switch to the **Matches** tab to see suggested partner businesses

---

## API Endpoints

| Method | Endpoint   | Description                        |
|--------|------------|------------------------------------|
| POST   | /analyze   | Analyze business data via GLM      |
| POST   | /chat      | Chat with AI using business context|

---

## Tech Stack

- **Frontend**: HTML + CSS + JavaScript (no framework)
- **Backend**: Python + FastAPI
- **AI**: GLM API (configurable)
- **Data**: JSON file (no database needed)
