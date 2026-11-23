# EchoWave

Accessible indoor navigation for visually impaired users. This version keeps the original React interface and adds a Python API that runs deep-learning object detection for the obstacle alert.

## Features

- A* indoor routing with spoken turn-by-turn directions
- Voice destination input, text-to-speech, QR location scanning, sign OCR, and manual location selection
- Step-counted turn-by-turn progression; supported motion sensors advance when the current instruction's step count is reached, with a `+1 step` control for desktop/no-sensor testing
- Multiple college floor maps, stair avoidance, SOS announcement, and pedometer
- Camera obstacle detection powered by **YOLOv8-Worldv2** open-vocabulary detection through a **FastAPI** Python backend; prompts include people, doors, desks, chairs, benches, stairs, and common obstacles

## Technology

- Frontend: React, JavaScript, CSS, Web Speech API, jsQR, Tesseract.js
- Backend: Python, FastAPI, Ultralytics YOLOv8-Worldv2, Pillow
- Routing: A* over the bundled building graph

## Start locally

Requires Node.js 16+ and Python 3.10 or 3.11. Open two terminals in the project folder.

**Terminal 1 — Python API:**

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — React frontend:**

```bash
npm install
npm start
```

Open `http://localhost:3000`. The React dev server forwards `/api` requests to `http://localhost:8000`. The YOLOv8-Worldv2 weights download automatically on the first detection request, so internet access is needed for initial model setup. The API health endpoint is `http://localhost:8000/api/health`.

## Camera notes

Allow camera access when prompted. Browsers generally require HTTPS for camera access on a phone; `localhost` is supported for development. The detector checks a custom list of indoor objects and gives left/center/right image-position alerts. Image area is only a rough urgency cue; it does not measure distance or guarantee that a walking path is clear. Detection can miss objects or misclassify them. Treat it as an experimental aid, not a safety device.

## Deploy to Vercel (frontend and API)

The repository is prepared for two Vercel projects connected to the same Git repository:

1. Push this folder's contents to a GitHub repository.
2. In Vercel, import the repository as the **frontend** project. Keep the root directory as `./`, framework preset as Create React App, build command `npm run build`, and output directory `build`.
3. Create a second Vercel project from that same repository. Set its root directory to `backend`; Vercel will use `backend/index.py` and `backend/requirements.txt` for FastAPI.
4. Copy the backend deployment's base URL (for example `https://echowave-api.vercel.app`). In the frontend project's Settings → Environment Variables, add `REACT_APP_API_URL` with that base URL, then redeploy the frontend.
5. Copy the frontend deployment URL. In the backend project's Settings → Environment Variables, add `CORS_ORIGINS` with that exact frontend origin (for example `https://echowave.vercel.app`), then redeploy the backend.

The model weights download on the API's first detection request. Vercel Hobby is free for personal, non-commercial use, with monthly compute quotas. YOLO inference is CPU-heavy and the app sends repeated frames, so expect cold starts, slower detection, and limited usage; keep obstacle detection off when you are not actively using it. Verify Vercel's current limits before deployment.

## Project layout

```text
backend/              FastAPI app and Python dependencies
src/                  React interface, navigation and camera client
src/data/             College floor graphs
src/utils/pathfinding.js  A* routing and instruction generation
```

## Add a college

Add the college's nodes, edges, and shortcuts in `src/data/colleges.js`.

## License

MIT
