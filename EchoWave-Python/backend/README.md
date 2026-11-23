# EchoWave Python backend

FastAPI serves an open-vocabulary YOLOv8-Worldv2 deep-learning detector used by the React obstacle alert. It prompts for people, doors, doorways, desks, chairs, benches, stairs, tables, boxes, bags, wheelchairs, canes, trash cans, bicycles, plants, and general obstacles. This broadens the classes beyond COCO's fixed list, but it does not guarantee correct detection in every scene.

## Run

Use Python 3.10 or 3.11, then from this `backend` folder:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The model weights (`yolov8s-worldv2.pt`) download automatically the first time `/api/detect` is called; that first inference needs internet access and may take longer. Check `http://localhost:8000/api/health`.

## API

- `GET /api/health` — backend status
- `POST /api/detect` — raw JPEG/PNG bytes with matching `Content-Type`; responds with detections, confidence, bounding boxes, left/center/right image position, and a rough image-area urgency flag. The image position is relative to the camera view, not a mapped indoor direction.

The React development server proxies `/api` to port 8000. For camera access on phones, browsers generally require HTTPS; local `localhost` is supported for development. Detection and position estimates can be wrong, especially with poor lighting, occlusion, unusual furniture, or small/distant objects. Alerts advise stopping and checking; suggested passing sides are conditional on the user confirming that side is clear. This experimental aid must not be relied on as a safety device. Fine-tuning on labeled images from the target building is needed for higher site-specific accuracy.
