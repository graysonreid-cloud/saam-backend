from fastapi import APIRouter, Depends
from db.database import get_db
from app.services.synthetic_sprint import generate_synthetic_sprint

router = APIRouter()

@router.post("/admin/generate-sprint")
def generate_sprint(db=Depends(get_db)):
    return generate_synthetic_sprint(db)
