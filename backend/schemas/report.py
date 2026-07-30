from pydantic import BaseModel
from typing import Optional


class ReportRequest(BaseModel):
    job_description_id: Optional[int] = None


class ReportResponse(BaseModel):
    message: str
    file_path: str
    download_url: str
    file_type: str
