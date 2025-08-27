from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    filename = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Composite index for efficient queries
    __table_args__ = (
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<Payslip(id={self.id}, employee_id={self.employee_id}, month={self.month}, year={self.year})>"
