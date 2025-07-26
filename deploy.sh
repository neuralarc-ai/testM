#!/bin/bash

# Manus AI Clone Deployment Script
# This script deploys the complete Manus AI clone system

set -e

echo "🚀 Starting Manus AI Clone Deployment..."

# Configuration
PROJECT_NAME="manus-ai-clone"
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        print_success "Docker is available"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker is not available - using local deployment"
        DOCKER_AVAILABLE=false
    fi
    
    print_success "Dependencies check completed"
}

# Build frontend
build_frontend() {
    print_status "Building frontend..."
    
    cd manus-frontend
    
    # Install dependencies
    npm install
    
    # Build for production
    npm run build
    
    print_success "Frontend built successfully"
    cd ..
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd manus-backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install -r requirements.txt
    
    print_success "Backend setup completed"
    cd ..
}

# Deploy with Docker
deploy_docker() {
    print_status "Deploying with Docker..."
    
    # Build and start containers
    docker-compose up -d --build
    
    print_success "Docker deployment completed"
}

# Deploy locally
deploy_local() {
    print_status "Deploying locally..."
    
    # Start backend
    cd manus-backend
    source venv/bin/activate
    nohup python src/main.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    cd ..
    
    # Start frontend (serve built files)
    cd manus-frontend
    nohup npx serve -s dist -l $FRONTEND_PORT > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    cd ..
    
    print_success "Local deployment completed"
    print_status "Backend running on port $BACKEND_PORT (PID: $BACKEND_PID)"
    print_status "Frontend running on port $FRONTEND_PORT (PID: $FRONTEND_PID)"
}

# Health check
health_check() {
    print_status "Performing health check..."
    
    # Wait for services to start
    sleep 5
    
    # Check backend
    if curl -f http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
        print_success "Backend is healthy"
    else
        print_error "Backend health check failed"
        return 1
    fi
    
    # Check frontend
    if curl -f http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        print_success "Frontend is healthy"
    else
        print_error "Frontend health check failed"
        return 1
    fi
    
    print_success "All services are healthy"
}

# Create systemd services (for production)
create_systemd_services() {
    print_status "Creating systemd services..."
    
    # Backend service
    sudo tee /etc/systemd/system/manus-backend.service > /dev/null <<EOF
[Unit]
Description=Manus AI Clone Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)/manus-backend
Environment=PATH=$(pwd)/manus-backend/venv/bin
ExecStart=$(pwd)/manus-backend/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Frontend service
    sudo tee /etc/systemd/system/manus-frontend.service > /dev/null <<EOF
[Unit]
Description=Manus AI Clone Frontend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)/manus-frontend
ExecStart=/usr/bin/npx serve -s dist -l $FRONTEND_PORT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable services
    sudo systemctl daemon-reload
    sudo systemctl enable manus-backend
    sudo systemctl enable manus-frontend
    
    print_success "Systemd services created"
}

# Main deployment function
main() {
    print_status "🤖 Manus AI Clone Deployment Starting..."
    
    check_dependencies
    
    # Build frontend
    build_frontend
    
    # Setup backend
    setup_backend
    
    # Choose deployment method
    if [ "$DOCKER_AVAILABLE" = true ] && [ -f "docker-compose.yml" ]; then
        deploy_docker
    else
        deploy_local
    fi
    
    # Health check
    if health_check; then
        print_success "🎉 Deployment completed successfully!"
        echo ""
        print_status "Access your Manus AI Clone at:"
        print_status "Frontend: http://localhost:$FRONTEND_PORT"
        print_status "Backend API: http://localhost:$BACKEND_PORT"
        echo ""
        print_status "API Documentation: http://localhost:$BACKEND_PORT/api"
        print_status "Health Check: http://localhost:$BACKEND_PORT/health"
        echo ""
        print_status "Logs:"
        print_status "Backend: tail -f backend.log"
        print_status "Frontend: tail -f frontend.log"
    else
        print_error "Deployment failed during health check"
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    "stop")
        print_status "Stopping services..."
        if [ -f "backend.pid" ]; then
            kill $(cat backend.pid) 2>/dev/null || true
            rm backend.pid
        fi
        if [ -f "frontend.pid" ]; then
            kill $(cat frontend.pid) 2>/dev/null || true
            rm frontend.pid
        fi
        if [ "$DOCKER_AVAILABLE" = true ]; then
            docker-compose down 2>/dev/null || true
        fi
        print_success "Services stopped"
        ;;
    "restart")
        $0 stop
        sleep 2
        $0
        ;;
    "status")
        print_status "Checking service status..."
        if curl -f http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
            print_success "Backend is running"
        else
            print_error "Backend is not running"
        fi
        if curl -f http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
            print_success "Frontend is running"
        else
            print_error "Frontend is not running"
        fi
        ;;
    "logs")
        print_status "Showing logs..."
        if [ -f "backend.log" ]; then
            echo "=== Backend Logs ==="
            tail -n 20 backend.log
        fi
        if [ -f "frontend.log" ]; then
            echo "=== Frontend Logs ==="
            tail -n 20 frontend.log
        fi
        ;;
    "systemd")
        create_systemd_services
        ;;
    *)
        main
        ;;
esac

