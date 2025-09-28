#!/bin/bash
# FADO CRM Development Environment Setup Script

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[SETUP] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

log "🚀 Setting up FADO CRM Development Environment"

# Check prerequisites
log "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    warn "Docker not found. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    warn "Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    warn "Docker is not running. Please start Docker first."
    exit 1
fi

log "✓ Prerequisites check passed"

# Create necessary directories
log "Creating necessary directories..."
mkdir -p logs uploads backend/logs backend/uploads ssl

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    log "Creating .env file from template..."
    cat > .env << EOF
# FADO CRM Development Environment
DATABASE_URL=postgresql://fado_user:fado_pass_2025@postgres:5432/fado_crm
REDIS_URL=redis://redis:6379
ENVIRONMENT=development
SECRET_KEY=dev-secret-key-change-in-production
STORAGE_DRIVER=local
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
VNPAY_TMN_CODE=DEMOVNP01
VNPAY_HASH_SECRET=VNPAYSECRETKEY2025
EOF
    log "✓ .env file created"
else
    log "✓ .env file already exists"
fi

# Build and start services
log "Building Docker images..."
docker-compose build

log "Starting services..."
docker-compose up -d

# Wait for services to be ready
log "Waiting for services to start..."
sleep 15

# Check if services are running
log "Checking service health..."
if docker-compose ps | grep -q "Up"; then
    log "✅ Services are running!"
else
    warn "❌ Some services failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Run database migrations
log "Running database migrations..."
docker-compose exec backend python -c "
from backend.database import engine, Base
from backend.models import *
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"

# Create admin user
log "Creating admin user..."
docker-compose exec backend python -c "
import sys
sys.path.append('/app')
from backend.auth import get_password_hash
from backend.database import SessionLocal
from backend.models import NguoiDung
from sqlalchemy.exc import IntegrityError

db = SessionLocal()
try:
    admin = NguoiDung(
        username='admin',
        email='admin@fado.vn',
        hashed_password=get_password_hash('admin123'),
        role='admin',
        is_active=True
    )
    db.add(admin)
    db.commit()
    print('Admin user created: admin@fado.vn / admin123')
except IntegrityError:
    print('Admin user already exists')
finally:
    db.close()
"

# Display status
log "🎉 Development environment setup complete!"
echo ""
echo "📋 Services Status:"
docker-compose ps
echo ""
echo "🌐 Access URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Database: localhost:5432"
echo "  Redis: localhost:6379"
echo ""
echo "👤 Default Login:"
echo "  Email: admin@fado.vn"
echo "  Password: admin123"
echo ""
echo "🔧 Useful Commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart services: docker-compose restart"
echo "  Enter backend container: docker-compose exec backend bash"
echo ""
log "Happy coding! 🚀"