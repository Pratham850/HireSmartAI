import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.report import ReportRequest, ReportResponse
from services.report_service import ReportService
from config import settings

router = APIRouter(prefix="/reports", tags=["7. Report Generation"])


@router.post(
    "/excel",
    response_model=ReportResponse,
    summary="Generate Excel Recruitment Report (.xlsx)",
    description="Generates styled Excel file containing candidate profiles, match scores, recommendations, and skills."
)
async def generate_excel_report(
    request: Optional[ReportRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    jd_id = request.job_description_id if request else None
    service = ReportService(db)
    return await service.generate_excel_report(jd_id)


@router.post(
    "/csv",
    response_model=ReportResponse,
    summary="Generate CSV Recruitment Report (.csv)",
    description="Generates CSV export of candidate evaluations and match ratings."
)
async def generate_csv_report(
    request: Optional[ReportRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    jd_id = request.job_description_id if request else None
    service = ReportService(db)
    return await service.generate_csv_report(jd_id)


@router.post(
    "/json",
    response_model=ReportResponse,
    summary="Generate JSON Summary Report (.json)",
    description="Generates complete structured JSON report export of campus recruitment data."
)
async def generate_json_report(
    request: Optional[ReportRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    jd_id = request.job_description_id if request else None
    service = ReportService(db)
    return await service.generate_json_report(jd_id)


@router.get(
    "/download/{filename}",
    summary="Download Generated Report File",
    description="Downloads specified report file (.xlsx, .csv, .json) from reports folder."
)
async def download_report(filename: str):
    # Security check to prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = os.path.join(settings.REPORT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
