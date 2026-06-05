from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pathlib
import uuid
import re
from datetime import datetime, timedelta

load_dotenv()

# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Return the current local time for a given city (best-effort).

    Uses UTC offsets or pytz to compute local times. Falls back to UTC.
    """
    # Map cities to UTC offsets (hours) as fallback
    offset_map = {
        "tokyo": 9,
        "india": 5.5,
        "asia": 5.5,
        "delhi": 5.5,
        "mumbai": 5.5,
        "dubai": 4,
        "london": 0,
        "new york": -5,
        "newyork": -5,
        "los angeles": -8,
        "losangeles": -8,
        "los_angeles": -8,
        "san francisco": -8,
        "sanfrancisco": -8,
        "sydney": 10,
    }

    name = (city or "").strip()
    # Normalize: lowercase, replace underscore/hyphen with space, remove trailing punctuation
    key = name.lower().replace("_", " ").replace("-", " ")
    key = re.sub(r"[\.,!?]$", "", key).strip()

    # Find offset
    offset = offset_map.get(key)
    
    # Fallback: match by substring
    if offset is None:
        for k in offset_map:
            if k in key:
                offset = offset_map[k]
                break

    # Compute local time
    utc_now = datetime.utcnow()
    
    if offset is not None:
        local_now = utc_now + timedelta(hours=offset)
        timestr = local_now.strftime('%I:%M %p').lstrip('0')
        return {"status": "success", "city": name, "time": timestr}
    
    # Fallback: return UTC time
    timestr = utc_now.strftime('%I:%M %p').lstrip('0')
    return {"status": "success", "city": name or "(unknown)", "time": timestr + ' UTC'}

app = FastAPI()

# Allow local browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = pathlib.Path(__file__).parent


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the local `agent.ui` file as the homepage."""
    ui_path = ROOT / "agent.ui"
    if ui_path.exists():
        return HTMLResponse(ui_path.read_text(encoding="utf-8"))
    return HTMLResponse("<html><body><h1>agent.ui not found</h1></body></html>")


@app.post("/apps/{app_name}/users/{user_id}/sessions")
async def create_session(app_name: str, user_id: str, request: Request):
    """Create a lightweight session object expected by the UI."""
    session_id = uuid.uuid4().hex
    return JSONResponse({"id": session_id})


@app.post("/run")
async def run_agent(request: Request):
    """Simple `/run` implementation that responds with an events array the UI expects.

    This is a minimal demo that extracts a city from the user's message and returns
    a simulated assistant reply using `get_current_time`.
    """
    body = await request.json()
    text = ""
    try:
        text = body.get("new_message", {}).get("parts", [])[0].get("text", "")
    except Exception:
        text = str(body)

    # Try to extract a city using a simple pattern: 'in <City>'
    m = re.search(r"in\s+([A-Za-z\s]+)\??$", text, re.IGNORECASE)
    city = m.group(1).strip() if m else text or "your city"

    result = get_current_time(city)
    reply = f"Current time in {result['city']}: {result['time']}"

    # Return a list of events similar to what the UI expects
    events = [{"content": {"parts": [{"text": reply}]}}]
    return JSONResponse(events)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)