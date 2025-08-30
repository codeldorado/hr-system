from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from .database import Base


class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    filename = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False, unique=True)
    file_size = Column(BigInteger, nullable=True)
    upload_timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Composite constraints and indexes for efficient queries
    __table_args__ = (
        # Unique constraint to prevent duplicate payslips for same employee/month/year
        UniqueConstraint("employee_id", "month", "year", name="uq_employee_month_year"),
        # Composite index for common query patterns
        Index("ix_employee_year_month", "employee_id", "year", "month"),
        Index("ix_year_month", "year", "month"),
        Index("ix_upload_timestamp_desc", upload_timestamp.desc()),
        {"extend_existing": True},
    )

    def __repr__(self):
        return (
            f"<Payslip(id={self.id}, employee_id={self.employee_id}, "
            f"month={self.month}, year={self.year})>"
        )
