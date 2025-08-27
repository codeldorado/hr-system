-- Database initialization script for payslip microservice
-- This script runs when the PostgreSQL container starts

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance (will be created by Alembic migrations)
-- This is just for reference

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE payslip_db TO postgres;

-- Create a read-only user for reporting (optional)
-- CREATE USER payslip_readonly WITH PASSWORD 'readonly_password';
-- GRANT CONNECT ON DATABASE payslip_db TO payslip_readonly;
-- GRANT USAGE ON SCHEMA public TO payslip_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO payslip_readonly;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO payslip_readonly;
