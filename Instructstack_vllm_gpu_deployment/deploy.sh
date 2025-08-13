#!/bin/bash

# =============================================================================
# VLLM GPU Deployment Script
# =============================================================================
# This script automates the complete deployment of the VLLM GPU-based inference
# stack with monitoring, logging, and web interface.
# =============================================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker and Docker Compose
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Prerequisites check passed!"
}

# Function to setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f "env-template.txt" ]; then
            print_status "Creating .env file from template..."
            cp env-template.txt .env
            print_warning "Please edit .env file with your actual configuration values!"
            print_warning "Especially update the LOGFIRE_TOKEN with your actual key."
            read -p "Press Enter after editing .env file to continue..."
        else
            print_error "env-template.txt not found. Cannot create .env file."
            exit 1
        fi
    else
        print_success ".env file already exists."
    fi
    
    # Validate LOGFIRE_TOKEN
    if grep -q "LOGFIRE_TOKEN=pylf_v1_eu_" .env; then
        print_warning "LOGFIRE_TOKEN appears to be a placeholder. Please update it with your actual key."
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p models
    mkdir -p prometheus
    mkdir -p logs
    
    print_success "Directories created successfully!"
}

# Function to download models
download_models() {
    print_status "Checking for models..."
    
    if [ ! -d "models/yasserrmd/Text2SQL-1.5B" ] && [ ! -d "models/premai-io/prem-1B-SQL" ]; then
        print_warning "No models found. Would you like to download them now? (y/n)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            print_status "Downloading models... This may take a while..."
            python3 download_model.py
            print_success "Models downloaded successfully!"
        else
            print_warning "Skipping model download. Make sure models are available before starting services."
        fi
    else
        print_success "Models already exist."
    fi
}

# Function to stop existing services
stop_services() {
    print_status "Stopping existing services..."
    
    if docker compose ps | grep -q "Up"; then
        docker compose down
        print_success "Existing services stopped."
    else
        print_status "No running services found."
    fi
}

# Function to start services
start_services() {
    print_status "Starting VLLM GPU stack..."
    
    # Start services in background
    docker composeup -d
    
    print_success "Services started successfully!"
    print_status "Waiting for services to be ready..."
    
    # Wait for services to be ready
    sleep 10
    
    # Check service status
    docker composeps
}

# Function to show service URLs
show_urls() {
    echo ""
    print_success "🎉 VLLM GPU Stack is now running!"
    echo ""
    echo "📊 Service URLs:"
    echo "  • VLLM API:        http://localhost:8000"
    echo "  • FastAPI Web:     http://localhost:9000"
    echo "  • Prometheus:      http://localhost:9090"
    echo "  • Grafana:         http://localhost:3000"
    echo "  • cAdvisor:        http://localhost:8081"
    echo "  • Node Exporter:   http://localhost:9100"
    echo "  • DCGM Exporter:   http://localhost:9400"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View logs:       docker composelogs -f"
    echo "  • Stop services:   docker composedown"
    echo "  • Restart:         docker composerestart"
    echo "  • Status:          docker composeps"
    echo ""
    echo "🧪 Test the API:"
    echo "  • Run concurrency test: python3 concurrency_test.py"
    echo ""
}

# Function to run health check
health_check() {
    print_status "Running health check..."
    
    # Wait a bit more for services to fully initialize
    sleep 15
    
    # Check if VLLM is responding
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "VLLM service is healthy!"
    else
        print_warning "VLLM service health check failed. It may still be starting up."
    fi
    
    # Check if FastAPI is responding
    if curl -s http://localhost:9000/health >/dev/null 2>&1; then
        print_success "FastAPI service is healthy!"
    else
        print_warning "FastAPI service health check failed. It may still be starting up."
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing service logs (Press Ctrl+C to exit)..."
    docker composelogs -f
}

# Main deployment function
main() {
    echo ""
    echo "🚀 VLLM GPU Stack Deployment Script"
    echo "=================================="
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Setup environment
    setup_environment
    
    # Create directories
    create_directories
    
    # Download models if needed
    download_models
    
    # Stop existing services
    stop_services
    
    # Start services
    start_services
    
    # Health check
    health_check
    
    # Show service URLs
    show_urls
    
    # Ask if user wants to see logs
    echo ""
    print_status "Would you like to see the service logs? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        show_logs
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -l, --logs     Show service logs"
    echo "  -s, --start    Start services only"
    echo "  -t, --stop     Stop services only"
    echo "  -r, --restart  Restart services"
    echo "  -c, --clean    Clean up everything (stop + remove containers)"
    echo ""
    echo "Examples:"
    echo "  $0              # Full deployment"
    echo "  $0 --start      # Start services only"
    echo "  $0 --logs       # Show logs only"
    echo "  $0 --stop       # Stop services"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -l|--logs)
        show_logs
        exit 0
        ;;
    -s|--start)
        start_services
        show_urls
        exit 0
        ;;
    -t|--stop)
        stop_services
        exit 0
        ;;
    -r|--restart)
        stop_services
        start_services
        health_check
        show_urls
        exit 0
        ;;
    -c|--clean)
        print_status "Cleaning up everything..."
        docker composedown -v --remove-orphans
        print_success "Cleanup completed!"
        exit 0
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
