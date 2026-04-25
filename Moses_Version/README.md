# BizMind — AI Business Advisor & Smart Matching Platform

A decision intelligence platform for young entrepreneurs and small business owners, built for UMHackathon 2026.

- 🎥 **Pitch Video:** https://youtu.be/YM-o8iqMK90
- 📋 **Trello Board:** [Insert URL here]

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, FastAPI
- **AI:** ILMU GLM (ilmu-glm-5.1)
- **Database:** JSON

## Getting Started

### Prerequisites

- Python 3.10+
- ILMU API key from [console.ilmu.ai](https://console.ilmu.ai)

### Installation

```bash
pip install fastapi uvicorn httpx
```

### Configuration

In `main.py`, set your API credentials:

```python
GLM_API_URL = "https://api.ilmu.ai/v1/chat/completions"
GLM_API_KEY = "your-api-key-here"
```

### Running the App

**Terminal 1 — Backend:**
```bash
python -m uvicorn main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
python -m http.server 3000
```

Open [http://localhost:3000/index.html](http://localhost:3000/index.html) in your browser.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/analyze` | Analyze business data and return AI insights |
| POST | `/recommend` | Get 3 actionable recommendations |
| POST | `/match` | Find relevant business partners |
| POST | `/chat` | Context-aware AI chat |

## Project Structure

```
project/
├── main.py
├── data/
│   └── businesses.json
├── frontend/
│   └── index.html
└── README.md
```

## Team

**Nomads** — UMHackathon 2026

| Name
|---|---|
| Mousa Alaa Mousa Nejmi
| Abdulrahman Abdullah Abdulrahman Al-Gafri
