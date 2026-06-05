Time Agent
==========

A small FastAPI-based demo that serves a chat-style UI (`agent.ui`) and returns the current local time for requested cities.

Quick start
-----------
1. Install dependencies (recommended in a virtualenv):

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install fastapi uvicorn python-dotenv
```

2. Run the app:

```powershell
cd C:\Users\Archents\my_agent
python web_agent.py
```

3. Open the UI in your browser:

http://127.0.0.1:8000/

What the project contains
------------------------
- `agent.ui` — The frontend HTML/CSS/JS chat UI. The UI calls the backend endpoints to create a session and post messages to `/run`.
- `web_agent.py` — FastAPI server that:
  - Serves `agent.ui` at `/`
  - Implements `POST /apps/{app_name}/users/{user_id}/sessions` to create a lightweight session
  - Implements `POST /run` which accepts the UI payload, extracts the city and returns a JSON events array the UI expects
  - Contains `get_current_time(city)` which maps common city names to UTC offsets and computes a local time for demo purposes
- `agent.py` — Example ADK agent definition (not currently wired into `web_agent.py`).

Endpoints (brief)
-----------------
- `GET /` — returns the `agent.ui` HTML page
- `POST /apps/{app_name}/users/{user_id}/sessions` — returns `{ "id": "<session-id>" }`
- `POST /run` — accepts JSON like the UI sends and returns an events array:

example request body:

```json
{
  "app_name": "my_agent",
  "user_id": "user_xxx",
  "session_id": "...",
  "new_message": { "role": "user", "parts": [{ "text": "What time is it in Tokyo?" }] }
}
```

example response body:

```json
[{"content":{"parts":[{"text":"Current time in Tokyo: 8:08 PM"}]}}]
```

Troubleshooting
---------------
- If you see `{"detail":"Not Found"}` opening `http://127.0.0.1:8000`, another process may be handling port 8000. Run:

```powershell
netstat -aon | findstr LISTENING | findstr :8000
```

then kill the PID:

```powershell
taskkill /F /PID <PID>
```

- If the UI looks offline, check the browser console for failed requests and ensure the `API` constant in `agent.ui` points to `http://127.0.0.1:8000`.

Extending the project
---------------------
- Plug the `root_agent` from `agent.py` into `/run` to process messages using ADK instead of the simple `get_current_time` tool.
- Replace the offset lookup with a real timezone database (`zoneinfo` or `pytz`) for robust DST handling.
- Add more cities to the `offset_map` in `web_agent.py`.

Files
-----
- [agent.ui](agent.ui)
- [web_agent.py](web_agent.py)
- [agent.py](agent.py)

License
-------
Small demo for local development. No license declared.
