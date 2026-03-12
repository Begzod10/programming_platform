from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db  # ✅ bir joydan import
from app.services import degree_service
from app.schemas.degree import (
    DegreeCreate, DegreeUpdate, DegreeRead,
    StudentDegreeRead, DegreeProgress, CertificateVerify
)
from typing import List

router = APIRouter()


@router.get("/", response_model=List[DegreeRead])
async def get_all_degrees(db: AsyncSession = Depends(get_db)):
    return await degree_service.get_all_degrees(db)


@router.get("/my", response_model=List[StudentDegreeRead])
async def my_degrees(student_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    degrees = await degree_service.get_my_degrees(db, student_id)
    return [
        StudentDegreeRead(
            id=sd.id,
            degree_name=sd.degree.name,
            degree_level=sd.degree.level,
            earned_at=sd.earned_at,
            verification_code=sd.verification_code,
            certificate_url=sd.certificate_url
        ) for sd in degrees
    ]


@router.get("/progress", response_model=List[DegreeProgress])
async def degree_progress(student_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    progress = await degree_service.get_degree_progress(db, student_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Student topilmadi")
    return progress


@router.get("/certificate/{verification_code}", response_model=CertificateVerify)
async def verify_certificate(verification_code: str, db: AsyncSession = Depends(get_db)):
    cert = await degree_service.verify_certificate(db, verification_code)
    if not cert:
        raise HTTPException(status_code=404, detail="Sertifikat topilmadi")
    return CertificateVerify(
        valid=True,
        student_name=cert.student.full_name,
        username=cert.student.username,
        degree_name=cert.degree.name,
        degree_level=cert.degree.level,
        earned_at=cert.earned_at,
        verification_code=cert.verification_code
    )


@router.get("/{degree_id}", response_model=DegreeRead)
async def get_degree(degree_id: int, db: AsyncSession = Depends(get_db)):
    degree = await degree_service.get_degree_by_id(db, degree_id)
    if not degree:
        raise HTTPException(status_code=404, detail="Daraja topilmadi")
    return degree


@router.post("/create", response_model=DegreeRead)
async def create_degree(data: DegreeCreate, db: AsyncSession = Depends(get_db)):
    return await degree_service.create_degree(
        db, data.name, data.description, data.level,
        data.required_points, data.required_projects,
        data.certificate_template, data.badge_image_url
    )


@router.put("/{degree_id}", response_model=DegreeRead)
async def update_degree(degree_id: int, data: DegreeUpdate, db: AsyncSession = Depends(get_db)):
    degree = await degree_service.update_degree(
        db, degree_id,
        name=data.name, description=data.description,
        level=data.level, required_points=data.required_points,
        required_projects=data.required_projects
    )
    if not degree:
        raise HTTPException(status_code=404, detail="Daraja topilmadi")
    return degree


@router.delete("/{degree_id}")
async def delete_degree(degree_id: int, db: AsyncSession = Depends(get_db)):
    result = await degree_service.delete_degree(db, degree_id)
    if not result:
        raise HTTPException(status_code=404, detail="Daraja topilmadi")
    return {"message": "Daraja o'chirildi!"}


@router.post("/award")
async def award_degree(
        student_id: int = Query(...),
        degree_id: int = Query(...),
        db: AsyncSession = Depends(get_db)
):
    result = await degree_service.award_degree(db, student_id, degree_id)
    if not result:
        raise HTTPException(status_code=400, detail="Daraja berib bo'lmadi yoki allaqachon mavjud")
    return {"message": "Daraja berildi!", "verification_code": result.verification_code}


@router.post("/check-and-award")
async def check_and_award(student_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    awarded = await degree_service.check_and_award_degrees(db, student_id)
    if not awarded:
        return {"message": "Yangi daraja yo'q", "awarded": []}
    return {
        "message": f"{len(awarded)} ta yangi daraja berildi!",
        "awarded": [{"verification_code": d.verification_code} for d in awarded]
    }