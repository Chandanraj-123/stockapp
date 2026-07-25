#!/bin/bash

# Test Script for Stock Market Dashboard
# This script helps debug and verify the Docker Compose setup

set -e

echo "=========================================="
echo "Stock Market Dashboard - Test Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print error
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to print success
print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to print info
print_info() {
    echo -e "[INFO] $1"
}

# Step 1: Check if Docker is running
echo ""
echo "Step 1: Checking Docker..."
if docker --version > /dev/null 2>&1; then
    print_success "Docker is installed"
else
    print_error "Docker is not installed or not running"
    exit 1
fi

# Step 2: Check if Docker Compose is installed
echo ""
echo "Step 2: Checking Docker Compose..."
if docker compose version > /dev/null 2>&1; then
    print_success "Docker Compose is installed"
else
    print_error "Docker Compose is not installed"
    exit 1
fi

# Step 3: Check repository structure
echo ""
echo "Step 3: Checking repository structure..."

# Check if services directory exists
if [ -d "services" ]; then
    print_success "services/ directory exists"
else
    print_error "services/ directory does not exist"
    exit 1
fi

# Check if frontend directory exists
if [ -d "frontend" ]; then
    print_success "frontend/ directory exists"
else
    print_error "frontend/ directory does not exist"
    exit 1
fi

# Check if shared-libs directory exists
if [ -d "shared-libs" ]; then
    print_success "shared-libs/ directory exists"
else
    print_error "shared-libs/ directory does not exist"
    exit 1
fi

# Check if docker-compose.yml exists
if [ -f "docker-compose.yml" ]; then
    print_success "docker-compose.yml exists"
else
    print_error "docker-compose.yml does not exist"
    exit 1
fi

# Step 4: Check all service directories
echo ""
echo "Step 4: Checking all service directories..."

SERVICES=(
    "api-gateway"
    "auth-service"
    "user-service"
    "market-data-service"
    "watchlist-service"
    "screener-service"
    "portfolio-service"
    "trading-service"
    "alert-service"
    "notification-service"
    "news-service"
    "scheduler-service"
    "reporting-service"
    "ai-service"
    "admin-dashboard"
)

for service in "${SERVICES[@]}"; do
    if [ -d "services/$service" ]; then
        print_success "services/$service/ exists"
    else
        print_error "services/$service/ does not exist"
        exit 1
    fi
done

# Step 5: Check required files in each service
echo ""
echo "Step 5: Checking required files in each service..."

REQUIRED_FILES=("main.py" "Dockerfile" "__init__.py")

for service in "${SERVICES[@]}"; do
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "services/$service/$file" ]; then
            print_success "services/$service/$file exists"
        else
            print_warning "services/$service/$file does not exist"
        fi
    done
done

# Step 6: Check frontend files
echo ""
echo "Step 6: Checking frontend files..."

FRONTEND_FILES=("package.json" "package-lock.json" "Dockerfile" "next.config.js" "tsconfig.json")

for file in "${FRONTEND_FILES[@]}"; do
    if [ -f "frontend/$file" ]; then
        print_success "frontend/$file exists"
    else
        print_error "frontend/$file does not exist"
        exit 1
    fi
done

# Step 7: Check .dockerignore
echo ""
echo "Step 7: Checking .dockerignore..."
if [ -f ".dockerignore" ]; then
    print_success ".dockerignore exists"
    
    # Check if shared-libs is excluded
    if grep -q "shared-libs/" .dockerignore; then
        print_error ".dockerignore excludes shared-libs/ (this will cause build errors)"
        exit 1
    else
        print_success "shared-libs/ is not excluded in .dockerignore"
    fi
else
    print_warning ".dockerignore does not exist (not critical)"
fi

# Step 8: Try to build with Docker Compose
echo ""
echo "Step 8: Testing Docker Compose build..."
print_info "This may take several minutes..."

# First, try to pull images
print_info "Pulling base images..."
docker compose pull 2>&1 | grep -E "(Pulled|Pulling|Downloaded)" || true

# Try to build
print_info "Building services..."
if docker compose build 2>&1; then
    print_success "Docker Compose build completed successfully"
else
    print_error "Docker Compose build failed"
    print_info "Checking build logs for errors..."
    
    # Check for specific errors
    if docker compose build 2>&1 | grep -q "not found"; then
        print_error "Build failed: File not found error detected"
        print_info "This usually means a file is missing or in the wrong location"
        exit 1
    fi
    
    if docker compose build 2>&1 | grep -q "The system cannot find the file specified"; then
        print_error "Build failed: System cannot find file"
        print_info "Check that all service directories exist"
        exit 1
    fi
    
    exit 1
fi

# Step 9: Try to start services
echo ""
echo "Step 9: Starting services with Docker Compose..."
print_info "This may take several minutes..."

if docker compose up -d 2>&1; then
    print_success "Docker Compose up completed successfully"
else
    print_error "Docker Compose up failed"
    exit 1
fi

# Step 10: Verify services are running
echo ""
echo "Step 10: Verifying services are running..."

# Wait for services to start
print_info "Waiting for services to start..."
sleep 10

# Check service status
SERVICE_PORTS=(
    "8000:api-gateway"
    "8001:auth-service"
    "8002:user-service"
    "8003:market-data-service"
    "8004:watchlist-service"
    "8005:screener-service"
    "8006:portfolio-service"
    "8007:trading-service"
    "8008:alert-service"
    "8009:notification-service"
    "8010:news-service"
    "8011:scheduler-service"
    "8012:reporting-service"
    "8013:ai-service"
    "8014:admin-dashboard"
    "3000:frontend"
)

for port_service in "${SERVICE_PORTS[@]}"; do
    IFS=':' read -r port service <<< "$port_service"
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/health" 2>/dev/null | grep -q "200"; then
        print_success "Service on port $port ($service) is healthy"
    else
        print_warning "Service on port $port ($service) is not responding or not healthy"
    fi
done

# Step 11: Show final status
echo ""
echo "=========================================="
echo "Test Script Complete"
echo "=========================================="
echo ""

docker compose ps 2>/dev/null || echo "Unable to show service status"

echo ""
echo "If you see any errors above, please check:"
echo "1. All service directories exist"
echo "2. All required files are in place"
echo "3. .dockerignore is not excluding needed files"
echo "4. Docker and Docker Compose are running"
echo ""
