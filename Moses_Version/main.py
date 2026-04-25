import json
import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


GLM_API_URL = "https://api.ilmu.ai/v1/chat/completions"
GLM_API_KEY = ""


#  GLM calling function — this is where we interact with the AI model

def call_glm(prompt: str) -> str:
    """Sends a prompt to the GLM API and returns the text response."""
    headers = {
        "Authorization": f"Bearer {GLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = json.dumps({
        "model": "ilmu-glm-5.1",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 800,
        "temperature": 0.7,
    })
    try:
        response = httpx.post(GLM_API_URL, headers=headers, content=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GLM API error: {str(e)}")



#backend analysis

def compute_sales_metrics(weekday: float, weekend: float) -> dict:
    """
    Performs real numerical analysis on sales data.
    Returns structured metrics before we even touch the GLM.
    """
    total = weekday + weekend
    difference = weekend - weekday

    # Calculate percentage difference
    if weekday > 0:
        pct_change = ((weekend - weekday) / weekday) * 100
    else:
        pct_change = 100.0

    # Identify best period
    if weekend > weekday:
        best_period = "Weekend"
        trend = "Weekend sales outperform weekday sales"
        direction = "up"
    elif weekday > weekend:
        best_period = "Weekday"
        trend = "Weekday sales outperform weekend sales"
        direction = "down"
        pct_change = ((weekday - weekend) / weekend) * 100 if weekend > 0 else 100.0
    else:
        best_period = "Equal"
        trend = "Weekday and weekend sales are equal"
        direction = "neutral"

    # Weekday vs weekend ratio
    weekday_pct = (weekday / total * 100) if total > 0 else 50
    weekend_pct = (weekend / total * 100) if total > 0 else 50

    # Average daily estimate (5 weekdays, 2 weekend days)
    avg_weekday_daily = weekday / 5
    avg_weekend_daily = weekend / 2

    return {
        "total_sales": round(total, 2),
        "difference": round(abs(difference), 2),
        "pct_change": round(abs(pct_change), 1),
        "best_period": best_period,
        "trend": trend,
        "direction": direction,
        "weekday_share": round(weekday_pct, 1),
        "weekend_share": round(weekend_pct, 1),
        "avg_weekday_daily": round(avg_weekday_daily, 2),
        "avg_weekend_daily": round(avg_weekend_daily, 2),
    }


def estimate_impact(metrics: dict) -> str:
    """
    Simulates revenue impact potential based on sales pattern.
    Simple rule-based logic — no AI needed here.
    """
    pct = metrics["pct_change"]
    direction = metrics["direction"]

    if direction == "up":
        # Weekend dominates — suggest boosting weekdays
        if pct > 100:
            return "Potential +20% revenue by improving weekday performance"
        elif pct > 50:
            return "Potential +15% revenue by improving weekday performance"
        else:
            return "Potential +10% revenue by balancing weekday strategy"
    elif direction == "down":
        # Weekday dominates — suggest boosting weekends
        if pct > 100:
            return "Potential +20% revenue by improving weekend performance"
        elif pct > 50:
            return "Potential +15% revenue by improving weekend performance"
        else:
            return "Potential +10% revenue by boosting weekend traffic"
    else:
        return "Potential +10% revenue by optimising peak hours"


def load_businesses():
    """Load the businesses JSON file."""
    data_path = "/Users/mousanajmi/Downloads/files/data/businesses.json"
    with open(data_path, "r") as f:
        return json.load(f)


def simple_match(description: str, businesses: list) -> list:
    """Basic keyword matching — returns up to 3 businesses."""
    desc_words = set(description.lower().split())
    matches = []
    for biz in businesses:
        service_words = set(biz["service_description"].lower().split())
        overlap = desc_words & service_words
        if overlap:
            matches.append({
                "name": biz["name"],
                "service_description": biz["service_description"],
                "overlap_keywords": list(overlap),
            })
    return matches[:3]


# ============================================================
#  REQUEST MODELS
# ============================================================
class AnalyzeRequest(BaseModel):
    description: str
    weekday_sales: float
    weekend_sales: float

class RecommendRequest(BaseModel):
    description: str
    weekday_sales: float
    weekend_sales: float

class MatchRequest(BaseModel):
    description: str
    weekday_sales: float
    weekend_sales: float

class ChatRequest(BaseModel):
    message: str
    description: str
    weekday_sales: float
    weekend_sales: float


# ============================================================
#  ENDPOINT 1: /analyze — Full decision intelligence pipeline
# ============================================================
@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """
    Full pipeline:
    1. Real backend analysis (no AI)
    2. Structured prompt built from computed metrics
    3. GLM provides reasoning on top of real data
    4. Returns structured insight/recommendation/explanation/impact
    """

    # Step 1: Real backend analysis
    metrics = compute_sales_metrics(req.weekday_sales, req.weekend_sales)
    impact = estimate_impact(metrics)

    # Step 2: Build a structured prompt using computed metrics
    prompt = f"""You are an AI business advisor helping young entrepreneurs in Malaysia make better decisions.

Business Description: {req.description}

Sales Data:
- Weekday Sales: RM {req.weekday_sales}
- Weekend Sales: RM {req.weekend_sales}
- Total Weekly Sales: RM {metrics['total_sales']}

Computed Analysis (already calculated — use this in your reasoning):
- {metrics['best_period']} is the best performing period
- {metrics['trend']}
- The difference is {metrics['pct_change']}% ({metrics['best_period']} is higher)
- Weekday contributes {metrics['weekday_share']}% of total sales
- Weekend contributes {metrics['weekend_share']}% of total sales
- Average daily weekday sales: RM {metrics['avg_weekday_daily']}
- Average daily weekend sales: RM {metrics['avg_weekend_daily']}

Based on this computed data, provide a structured response in EXACTLY this format:

INSIGHT:
[1-2 sentences about what the data pattern means for this specific business]

RECOMMENDATION:
[2 specific, actionable steps the owner should take based on the numbers]

EXPLANATION:
[2-3 sentences explaining the reasoning behind your recommendation]"""

    glm_response = call_glm(prompt)

    # Step 3: Parse GLM response into structured sections
    insight = ""
    recommendation = ""
    explanation = ""
    current_section = None

    for line in glm_response.splitlines():
        line = line.strip()
        if line.startswith("INSIGHT:"):
            current_section = "insight"
            rest = line.replace("INSIGHT:", "").strip()
            if rest:
                insight += rest + " "
        elif line.startswith("RECOMMENDATION:"):
            current_section = "recommendation"
            rest = line.replace("RECOMMENDATION:", "").strip()
            if rest:
                recommendation += rest + " "
        elif line.startswith("EXPLANATION:"):
            current_section = "explanation"
            rest = line.replace("EXPLANATION:", "").strip()
            if rest:
                explanation += rest + " "
        elif line and current_section:
            if current_section == "insight":
                insight += line + " "
            elif current_section == "recommendation":
                recommendation += line + " "
            elif current_section == "explanation":
                explanation += line + " "

    # Fallback if parsing fails
    if not insight:
        insight = glm_response
        recommendation = "See full response above."
        explanation = ""

    return {
        "insight": insight.strip(),
        "recommendation": recommendation.strip(),
        "explanation": explanation.strip(),
        "impact": impact,
        "metrics": metrics,
    }


# ============================================================
#  ENDPOINT 2: /recommend — Focused recommendations only
# ============================================================
@app.post("/recommend")
async def recommend(req: RecommendRequest):
    """
    Focused endpoint: returns only actionable recommendations.
    Uses computed metrics to make GLM answers more specific.
    """
    metrics = compute_sales_metrics(req.weekday_sales, req.weekend_sales)

    prompt = f"""You are an AI business advisor for young entrepreneurs in Malaysia.

Business: {req.description}
Best period: {metrics['best_period']} ({metrics['pct_change']}% higher)
Weekday daily average: RM {metrics['avg_weekday_daily']}
Weekend daily average: RM {metrics['avg_weekend_daily']}

Give exactly 3 specific, practical recommendations to improve revenue for this business.
Format as:
1. [First recommendation]
2. [Second recommendation]
3. [Third recommendation]

Keep each recommendation to 1-2 sentences. Be specific to the business type."""

    glm_response = call_glm(prompt)

    return {
        "recommendations": glm_response,
        "metrics": metrics,
        "impact": estimate_impact(metrics),
    }


# ============================================================
#  ENDPOINT 3: /match — Smart partner matching with GLM explanation
# ============================================================
@app.post("/match")
async def match(req: MatchRequest):
    """
    Finds keyword-matched businesses, then uses GLM to explain
    why each match is a good partnership — not just keyword overlap.
    """
    businesses = load_businesses()
    raw_matches = simple_match(req.description, businesses)

    if not raw_matches:
        return {"matches": []}

    enriched_matches = []
    for biz in raw_matches:
        # Use GLM to explain the partnership value
        prompt = f"""In 1-2 sentences, explain why this is a useful business partnership:

Business A: {req.description}
Business B: {biz['name']} — {biz['service_description']}
Shared keywords: {', '.join(biz['overlap_keywords'])}

Be specific and practical. Start with "This partnership..."."""

        explanation = call_glm(prompt)

        enriched_matches.append({
            "name": biz["name"],
            "service_description": biz["service_description"],
            "partnership_explanation": explanation,
        })

    return {"matches": enriched_matches}


# ============================================================
#  ENDPOINT 4: /chat — Contextual chat with computed metrics
# ============================================================
@app.post("/chat")
async def chat(req: ChatRequest):
    """
    Chat that includes both raw data AND computed metrics as context,
    so the GLM gives smarter, more specific answers.
    """
    metrics = compute_sales_metrics(req.weekday_sales, req.weekend_sales)

    prompt = f"""You are an AI business advisor for young entrepreneurs in Malaysia.

User's business context:
- Business: {req.description}
- Weekday Sales: RM {req.weekday_sales} (avg RM {metrics['avg_weekday_daily']}/day)
- Weekend Sales: RM {req.weekend_sales} (avg RM {metrics['avg_weekend_daily']}/day)
- Best performing period: {metrics['best_period']} ({metrics['pct_change']}% higher)
- Total weekly sales: RM {metrics['total_sales']}

User question: "{req.message}"

Give a helpful, practical, and encouraging answer in 2-4 sentences.
Reference their actual numbers where relevant."""

    glm_response = call_glm(prompt)
    return {"response": glm_response}
