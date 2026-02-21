from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.pipeline.service import PipelineService

router = APIRouter()


@router.post("/snapshot")
async def snapshot(
    request: Request,
    image: UploadFile,
    camera_id: str = Form(...),
    db: Session = Depends(get_db),
):
    image_bytes = await image.read()
    service = PipelineService(db=db, detector=request.app.state.detector)
    try:
        count = service.process(image_bytes, camera_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"camera_id": camera_id, "people_count": count}
