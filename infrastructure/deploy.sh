#!/bin/bash

# Terraform deployment script for payslip microservice infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="dev"
ACTION="plan"
AUTO_APPROVE=false

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENVIRONMENT    Environment to deploy (dev, staging, prod). Default: dev"
    echo "  -a, --action ACTION             Terraform action (plan, apply, destroy). Default: plan"
    echo "  --auto-approve                  Auto approve terraform apply/destroy"
    echo "  -h, --help                      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -e dev -a plan                # Plan deployment for dev environment"
    echo "  $0 -e prod -a apply --auto-approve  # Apply changes to prod with auto-approve"
    echo "  $0 -e dev -a destroy             # Destroy dev environment"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -a|--action)
            ACTION="$2"
            shift 2
            ;;
        --auto-approve)
            AUTO_APPROVE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT. Must be one of: dev, staging, prod"
    exit 1
fi

# Validate action
if [[ ! "$ACTION" =~ ^(plan|apply|destroy|init|validate)$ ]]; then
    print_error "Invalid action: $ACTION. Must be one of: plan, apply, destroy, init, validate"
    exit 1
fi

# Check if required tools are installed
command -v terraform >/dev/null 2>&1 || { print_error "terraform is required but not installed. Aborting."; exit 1; }
command -v aws >/dev/null 2>&1 || { print_error "aws cli is required but not installed. Aborting."; exit 1; }

# Set working directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_status "Starting Terraform $ACTION for $ENVIRONMENT environment..."

# Check if tfvars file exists
TFVARS_FILE="environments/${ENVIRONMENT}.tfvars"
if [[ ! -f "$TFVARS_FILE" ]]; then
    print_error "Environment file not found: $TFVARS_FILE"
    exit 1
fi

# Check for required environment variables
if [[ "$ACTION" == "apply" || "$ACTION" == "plan" ]]; then
    if [[ -z "$TF_VAR_db_password" ]]; then
        print_warning "TF_VAR_db_password not set. You will be prompted for database password."
    fi
fi

# Initialize Terraform if .terraform directory doesn't exist
if [[ ! -d ".terraform" ]]; then
    print_status "Initializing Terraform..."
    terraform init
fi

# Validate Terraform configuration
if [[ "$ACTION" != "init" ]]; then
    print_status "Validating Terraform configuration..."
    terraform validate
fi

# Execute the requested action
case $ACTION in
    init)
        print_status "Initializing Terraform..."
        terraform init
        ;;
    validate)
        print_status "Validating Terraform configuration..."
        terraform validate
        print_status "Configuration is valid!"
        ;;
    plan)
        print_status "Planning Terraform deployment..."
        terraform plan -var-file="$TFVARS_FILE" -out="terraform-${ENVIRONMENT}.tfplan"
        print_status "Plan saved to terraform-${ENVIRONMENT}.tfplan"
        ;;
    apply)
        if [[ "$AUTO_APPROVE" == true ]]; then
            print_status "Applying Terraform changes with auto-approve..."
            terraform apply -var-file="$TFVARS_FILE" -auto-approve
        else
            print_status "Applying Terraform changes..."
            terraform apply -var-file="$TFVARS_FILE"
        fi
        print_status "Deployment completed successfully!"
        
        # Show important outputs
        print_status "Important outputs:"
        terraform output alb_url
        terraform output s3_bucket_name
        ;;
    destroy)
        print_warning "This will destroy all resources in the $ENVIRONMENT environment!"
        if [[ "$AUTO_APPROVE" == true ]]; then
            print_status "Destroying infrastructure with auto-approve..."
            terraform destroy -var-file="$TFVARS_FILE" -auto-approve
        else
            terraform destroy -var-file="$TFVARS_FILE"
        fi
        print_status "Infrastructure destroyed successfully!"
        ;;
esac

print_status "Terraform $ACTION completed for $ENVIRONMENT environment."
