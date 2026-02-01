from fastapi import APIRouter, UploadFile, File
import uuid, shutil
from backend.services.detection_service import detection_service
from backend.services.change_detection import ChangeDetector
from backend.utils.database import db
from backend.config import settings

router = APIRouter(prefix="/api/v1")
cd = ChangeDetector()

@router.post("/detect")
async def detect(file: UploadFile = File(...)):
    tid = str(uuid.uuid4())
    path = settings.UPLOAD_DIR / f"{tid}_{file.filename}"
    with path.open("wb") as b: shutil.copyfileobj(file.file, b)
    return await detection_service.process_file(tid, path)

@router.post("/compare")
async def compare(f1: UploadFile = File(...), f2: UploadFile = File(...)):
    p1, p2 = settings.UPLOAD_DIR / f1.filename, settings.UPLOAD_DIR / f2.filename
    with p1.open("wb") as b: shutil.copyfileobj(f1.file, b)
    with p2.open("wb") as b: shutil.copyfileobj(f2.file, b)
    return cd.compare(str(p1), str(p2))

@router.get("/tasks")
async def get_tasks():
    return db.get_all()