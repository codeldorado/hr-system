#!/bin/bash

# Development environment setup script for payslip microservice

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

print_info "Setting up development environment for Payslip Microservice..."

# Check required tools
print_info "Checking required tools..."

if ! command_exists docker; then
    print_error "Docker is not installed. Please install Docker and try again."
    exit 1
fi

if ! command_exists docker-compose; then
    print_error "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.11+ and try again."
    exit 1
fi

if ! command_exists pip; then
    print_error "pip is not installed. Please install pip and try again."
    exit 1
fi

check_docker
print_success "All required tools are available"

# Set up Python virtual environment
print_info "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate 2>/dev/null || {
    print_error "Failed to activate virtual environment"
    exit 1
}

# Install Python dependencies
print_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt 2>/dev/null || {
    print_warning "requirements-dev.txt not found, installing development packages manually"
    pip install pytest pytest-cov black flake8 isort pre-commit
}

print_success "Python dependencies installed"

# Set up pre-commit hooks
print_info "Setting up pre-commit hooks..."
if command_exists pre-commit; then
    pre-commit install
    print_success "Pre-commit hooks installed"
else
    print_warning "pre-commit not available, skipping hook installation"
fi

# Create .env file if it doesn't exist
print_info "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_success "Created .env file from template"
    print_warning "Please update .env file with your configuration"
else
    print_info ".env file already exists"
fi

# Start infrastructure services
print_info "Starting infrastructure services (PostgreSQL, Redis, LocalStack)..."
docker-compose up -d postgres redis localstack

# Wait for services to be ready
print_info "Waiting for services to be ready..."
sleep 10

# Check if services are healthy
if docker-compose ps | grep -q "unhealthy"; then
    print_warning "Some services may not be fully ready. Check with: docker-compose ps"
else
    print_success "Infrastructure services are running"
fi

# Initialize database
print_info "Initializing database..."
if python scripts/init_db.py; then
    print_success "Database initialized successfully"
else
    print_warning "Database initialization failed. You may need to run it manually."
fi

# Run database migrations
print_info "Running database migrations..."
if alembic upgrade head; then
    print_success "Database migrations completed"
else
    print_warning "Database migrations failed. You may need to run them manually."
fi

# Create S3 bucket in LocalStack
print_info "Setting up S3 bucket in LocalStack..."
sleep 5  # Wait for LocalStack to be fully ready
aws --endpoint-url=http://localhost:4566 s3 mb s3://payslip-storage-bucket 2>/dev/null || {
    print_warning "Failed to create S3 bucket. LocalStack may not be ready yet."
}

# Run tests to verify setup
print_info "Running tests to verify setup..."
if pytest tests/ -v --tb=short; then
    print_success "All tests passed! Setup is complete."
else
    print_warning "Some tests failed. Please check the output above."
fi

# Display helpful information
echo ""
print_success "Development environment setup complete!"
echo ""
print_info "Next steps:"
echo "  1. Update .env file with your configuration"
echo "  2. Start the development server:"
echo "     python -m uvicorn app.main:app --reload"
echo "  3. Or use Docker Compose for development:"
echo "     docker-compose --profile dev up app-dev"
echo ""
print_info "Useful commands:"
echo "  - Run tests: pytest"
echo "  - Format code: black app/ tests/"
echo "  - Lint code: flake8 app/"
echo "  - Sort imports: isort app/ tests/"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo ""
print_info "Access points:"
echo "  - Application: http://localhost:8000"
echo "  - API Documentation: http://localhost:8000/docs"
echo "  - Health Check: http://localhost:8000/health"
echo ""
print_success "Happy coding! 🚀"
