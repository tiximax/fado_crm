#!/bin/bash
# FADO CRM Production Deployment Script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="fado-crm"
BACKUP_DIR="/opt/backups/fado-crm"
LOG_FILE="/var/log/fado-crm-deploy.log"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a $LOG_FILE
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a $LOG_FILE
    exit 1
}

# Pre-deployment checks
pre_deploy_checks() {
    log "Running pre-deployment checks..."

    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running"
    fi

    # Check if docker-compose is available
    if ! command -v docker-compose >/dev/null 2>&1; then
        error "docker-compose is not installed"
    fi

    # Check environment file
    if [ ! -f ".env.production" ]; then
        warn ".env.production not found, using default values"
    fi

    log "Pre-deployment checks passed ✓"
}

# Database backup
backup_database() {
    log "Creating database backup..."

    # Create backup directory
    mkdir -p $BACKUP_DIR

    # Backup timestamp
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)

    # Create database backup
    docker-compose exec -T postgres pg_dump -U fado_user fado_crm > "$BACKUP_DIR/fado_crm_$BACKUP_TIMESTAMP.sql"

    # Compress backup
    gzip "$BACKUP_DIR/fado_crm_$BACKUP_TIMESTAMP.sql"

    log "Database backup created: fado_crm_$BACKUP_TIMESTAMP.sql.gz"
}

# Build and deploy
deploy() {
    log "Starting deployment..."

    # Pull latest code (if git repo)
    if [ -d ".git" ]; then
        log "Pulling latest code..."
        git pull origin main
    fi

    # Build new images
    log "Building Docker images..."
    docker-compose -f docker-compose.prod.yml build --no-cache

    # Stop old containers gracefully
    log "Stopping old containers..."
    docker-compose -f docker-compose.prod.yml down --timeout 30

    # Start new containers
    log "Starting new containers..."
    docker-compose -f docker-compose.prod.yml up -d

    # Wait for health checks
    log "Waiting for services to be healthy..."
    sleep 30

    # Verify deployment
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up (healthy)"; then
        log "Deployment successful ✓"
    else
        error "Deployment failed - some services are not healthy"
    fi
}

# Database migrations
run_migrations() {
    log "Running database migrations..."

    # Run Alembic migrations inside container
    docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

    log "Database migrations completed ✓"
}

# Post-deployment tasks
post_deploy() {
    log "Running post-deployment tasks..."

    # Clear cache
    docker-compose -f docker-compose.prod.yml exec backend python -c "
import redis
r = redis.Redis(host='redis', port=6379, db=0)
r.flushdb()
print('Cache cleared')
    "

    # Cleanup old images
    docker image prune -f

    log "Post-deployment tasks completed ✓"
}

# Health check
health_check() {
    log "Performing health check..."

    # Check backend health
    if curl -f http://localhost/health >/dev/null 2>&1; then
        log "Backend health check passed ✓"
    else
        error "Backend health check failed"
    fi

    # Check frontend
    if curl -f http://localhost >/dev/null 2>&1; then
        log "Frontend health check passed ✓"
    else
        error "Frontend health check failed"
    fi

    log "All health checks passed ✓"
}

# Rollback function
rollback() {
    warn "Rolling back deployment..."

    # Stop current containers
    docker-compose -f docker-compose.prod.yml down

    # Restore from backup
    LATEST_BACKUP=$(ls -t $BACKUP_DIR/fado_crm_*.sql.gz | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        log "Restoring database from $LATEST_BACKUP"
        gunzip -c "$LATEST_BACKUP" | docker-compose -f docker-compose.prod.yml exec -T postgres psql -U fado_user -d fado_crm
    fi

    # Start previous version (implement version tagging for full rollback)
    docker-compose -f docker-compose.prod.yml up -d

    warn "Rollback completed"
}

# Main deployment process
main() {
    log "Starting FADO CRM deployment process..."

    # Trap errors for rollback
    trap 'error "Deployment failed! Run ./deploy.sh rollback to revert changes"' ERR

    case "${1:-deploy}" in
        "deploy")
            pre_deploy_checks
            backup_database
            deploy
            run_migrations
            post_deploy
            health_check
            log "🎉 Deployment completed successfully!"
            ;;
        "rollback")
            rollback
            ;;
        "health")
            health_check
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|health}"
            echo "  deploy  - Full deployment process (default)"
            echo "  rollback - Rollback to previous version"
            echo "  health  - Run health checks only"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"