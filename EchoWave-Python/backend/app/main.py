"""EchoWave API: YOLOv8-based obstacle detection for camera frames."""

from functools import lru_cache
from io import BytesIO
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from ultralytics import YOLO

app = FastAPI(title="EchoWave API", version="1.0.0")
configured_origins = os.getenv("CORS_ORIGINS", "")
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    *[origin.strip().rstrip("/") for origin in configured_origins.split(",") if origin.strip()],
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


TARGET_CLASSES = [
    "person", "door", "open door", "closed door", "doorway",
    "desk", "chair", "bench", "stairs", "staircase", "table",
    "box", "backpack", "suitcase", "wheelchair", "walking cane",
    "trash can", "bicycle", "potted plant", "obstacle",
]


@lru_cache(maxsize=1)
def get_model() -> YOLO:
    # Open-vocabulary YOLO-World supports indoor objects beyond COCO's fixed labels.
    model = YOLO("yolov8s-worldv2.pt")
    model.set_classes(TARGET_CLASSES)
    return model


@app.get("/api/health")
def health():
    return {"status": "ok", "model": "YOLOv8s-Worldv2", "classes": TARGET_CLASSES}


@app.post("/api/detect")
async def detect(request: Request):
    content_type = request.headers.get("content-type", "")
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Send an image/jpeg camera frame.")

    payload = await request.body()
    if not payload or len(payload) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image is empty or exceeds the 8 MB limit.")
    try:
        image = Image.open(BytesIO(payload)).convert("RGB")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="Could not decode image.")

    try:
        prediction = get_model().predict(image, conf=0.18, iou=0.5, imgsz=512, max_det=20, verbose=False)[0]
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Model inference failed: {exc}") from exc

    width, height = image.size
    detections = []
    for box in prediction.boxes:
        x1, y1, x2, y2 = (float(value) for value in box.xyxy[0].tolist())
        confidence = float(box.conf[0])
        label_id = int(box.cls[0])
        label = prediction.names[label_id]
        box_width = max(0.0, x2 - x1)
        box_height = max(0.0, y2 - y1)
        area_ratio = box_width * box_height / (width * height)
        center_x = (x1 + x2) / 2 / width
        direction = "left" if center_x < 0.4 else "right" if center_x > 0.6 else "center"
        detections.append({
            "label": label,
            "confidence": round(confidence, 3),
            "box": [round(x1), round(y1), round(x2), round(y2)],
            "direction": direction,
            # Image footprint is only a coarse urgency cue, not a distance measurement.
            "proximity": "near" if area_ratio >= 0.08 else "visible",
            "is_close": area_ratio >= 0.08,
        })

    return {"width": width, "height": height, "detections": detections}
