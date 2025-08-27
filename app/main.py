from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
from datetime import datetime
import uuid

from . import models, schemas, database
from .database import get_db
from .services import s3_service

app = FastAPI(
    title="Payslip Microservice",
    description="HR Platform Payslip Management Service",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    models.Base.metadata.create_all(bind=database.engine)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Payslip Microservice is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "payslip-microservice"
    }

@app.post("/payslips", response_model=schemas.PayslipResponse)
async def upload_payslip(
    employee_id: int = Form(...),
    month: int = Form(...),
    year: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a payslip PDF file
    
    - **employee_id**: Employee identifier
    - **month**: Month (1-12)
    - **year**: Year (e.g., 2024)
    - **file**: PDF file to upload
    """
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Validate month
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    # Check if payslip already exists for this employee/month/year
    existing_payslip = db.query(models.Payslip).filter(
        models.Payslip.employee_id == employee_id,
        models.Payslip.month == month,
        models.Payslip.year == year
    ).first()
    
    if existing_payslip:
        raise HTTPException(
            status_code=409, 
            detail=f"Payslip already exists for employee {employee_id} for {month}/{year}"
        )
    
    try:
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"payslips/{employee_id}/{year}/{month}/{uuid.uuid4()}.{file_extension}"
        
        # Upload to S3
        file_url = await s3_service.upload_file(file, unique_filename)
        
        # Create database record
        db_payslip = models.Payslip(
            employee_id=employee_id,
            month=month,
            year=year,
            filename=file.filename,
            file_url=file_url,
            file_size=file.size,
            upload_timestamp=datetime.utcnow()
        )
        
        db.add(db_payslip)
        db.commit()
        db.refresh(db_payslip)
        
        return db_payslip
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload payslip: {str(e)}")

@app.get("/payslips", response_model=List[schemas.PayslipResponse])
async def get_payslips(
    employee_id: int = None,
    year: int = None,
    month: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve payslips with optional filtering
    
    - **employee_id**: Filter by employee ID
    - **year**: Filter by year
    - **month**: Filter by month
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    
    query = db.query(models.Payslip)
    
    # Apply filters
    if employee_id:
        query = query.filter(models.Payslip.employee_id == employee_id)
    if year:
        query = query.filter(models.Payslip.year == year)
    if month:
        query = query.filter(models.Payslip.month == month)
    
    # Order by most recent first
    query = query.order_by(models.Payslip.upload_timestamp.desc())
    
    # Apply pagination
    payslips = query.offset(skip).limit(limit).all()
    
    return payslips

@app.get("/payslips/{payslip_id}", response_model=schemas.PayslipResponse)
async def get_payslip(payslip_id: int, db: Session = Depends(get_db)):
    """Get a specific payslip by ID"""
    
    payslip = db.query(models.Payslip).filter(models.Payslip.id == payslip_id).first()
    
    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")
    
    return payslip

@app.delete("/payslips/{payslip_id}")
async def delete_payslip(payslip_id: int, db: Session = Depends(get_db)):
    """Delete a payslip (admin only - implement proper auth)"""
    
    payslip = db.query(models.Payslip).filter(models.Payslip.id == payslip_id).first()
    
    if not payslip:
        raise HTTPException(status_code=404, detail="Payslip not found")
    
    try:
        # Delete from S3
        await s3_service.delete_file(payslip.file_url)
        
        # Delete from database
        db.delete(payslip)
        db.commit()
        
        return {"message": "Payslip deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete payslip: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
