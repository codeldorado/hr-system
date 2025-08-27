from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

class PayslipBase(BaseModel):
    employee_id: int
    month: int
    year: int
    filename: str

    @validator('month')
    def validate_month(cls, v):
        if v < 1 or v > 12:
            raise ValueError('Month must be between 1 and 12')
        return v

    @validator('year')
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v < 2000 or v > current_year + 1:
            raise ValueError(f'Year must be between 2000 and {current_year + 1}')
        return v

class PayslipCreate(PayslipBase):
    pass

class PayslipResponse(PayslipBase):
    id: int
    file_url: str
    file_size: Optional[int] = None
    upload_timestamp: datetime

    class Config:
        from_attributes = True

class PayslipFilter(BaseModel):
    employee_id: Optional[int] = None
    year: Optional[int] = None
    month: Optional[int] = None
    skip: int = 0
    limit: int = 100

    @validator('limit')
    def validate_limit(cls, v):
        if v > 1000:
            raise ValueError('Limit cannot exceed 1000')
        return v

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
