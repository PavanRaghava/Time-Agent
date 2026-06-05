Code Explanation — Time Agent
=============================

Overview
--------
This document explains the code in the `my_agent` workspace and how pieces interact.

Files
-----
- `web_agent.py` — Main backend. Serves UI and provides `/run` and session endpoints.
- `agent.ui` — Frontend single-file UI implemented in HTML/CSS/JS.
- `agent.py` — Example ADK agent definition (optional integration).

web_agent.py — detailed
-----------------------
1. Imports & configuration
   - `FastAPI`, `uvicorn` run the application.
   - `CORS` middleware is enabled for local testing.

2. `get_current_time(city: str) -> dict`
   - Purpose: return a dictionary with `status`, normalized `city` string and `time` string.
   - Implementation: a small `offset_map` maps common city names to UTC offsets (hours, fractional allowed for 30-minute offsets).
   - Normalization: input city strings are lowercased and underscores/hyphens become spaces so `Los_Angeles`, `los-angeles` and `Los Angeles` all match.
   - Behavior: If a mapping is found, the function computes `local_time = UTC + offset` and returns a formatted time. If no mapping, returns UTC time with label.

3. Endpoints
   - `GET /` — Loads and returns `agent.ui` from the repo root. If missing, returns a small HTML error.
   - `POST /apps/{app_name}/users/{user_id}/sessions` — Returns a random UUID session id. The UI expects this when initializing.
   - `POST /run` — Core endpoint: it accepts a JSON body that the UI sends, extracts `new_message.parts[0].text`, finds a city using `re.search(r"in\s+([A-Za-z\s]+)\??$", text)`, calls `get_current_time(city)` and returns an events list where each event contains `content.parts[text]` with the reply string.

agent.ui — detailed
-------------------
- Initializes by creating a session via `POST /apps/my_agent/users/{user_id}/sessions` and stores the returned `session_id`.
- When user submits a message, it sends a `POST /run` request with the payload the backend handles.
- The UI renders replies by iterating the returned events array and concatenating `parts[*].text`.

agent.py — detailed
-------------------
- Shows how to create a Google ADK `Agent` named `root_agent` with a `get_current_time` tool. This demonstrates integration but is not wired into `web_agent.py` by default.

How the message format flows
---------------------------
1. UI sends `POST /run` with JSON containing `new_message.parts[0].text`.
2. Backend extracts the text, determines the city, computes a reply string.
3. Backend returns an array of event objects with `content.parts` containing text fragments.
4. UI parses the events and displays them in the chat.

Extending & Production notes
----------------------------
- For production, replace the offset map with real timezone lookups using `zoneinfo` or `pytz` to properly handle DST.
- Validate inputs and sanitize text before using regex extraction.
- Add authentication if exposing the endpoint publicly.

Example curl usage
------------------
Create session:

```bash
curl -X POST "http://127.0.0.1:8000/apps/my_agent/users/me/sessions" -H "Content-Type: application/json" -d '{}'
```

Run a query:

```bash
curl -X POST "http://127.0.0.1:8000/run" -H "Content-Type: application/json" -d '{"app_name":"my_agent","user_id":"user_x","session_id":"abc","new_message":{"role":"user","parts":[{"text":"What time is it in Tokyo?"}]}}'
```

Tips
----
- Add more friendly parsing rules to `run_agent` to robustly extract city names (NLP or a list of city aliases).
- Replace the demo reply with the `root_agent` from `agent.py` for more advanced behavior.

Contact
-------
If you want, I can wire `agent.py` into `web_agent.py` so the backend forwards message text to the ADK agent and streams real model responses back to the UI.