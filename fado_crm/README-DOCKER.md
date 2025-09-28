# 🐳 FADO CRM - Docker Production Setup

## 📋 Quick Start

### Development Environment
```bash
# Clone repository
git clone <repo-url>
cd fado_crm

# Setup development environment (automated)
./scripts/setup-dev.sh

# Or manual setup
docker-compose up -d
```

### Production Environment
```bash
# Copy environment file
cp .env.production.example .env.production
# Edit .env.production with your production values

# Deploy to production
./scripts/deploy.sh deploy
```

## 🏗️ Architecture

### Services Overview
- **postgres**: PostgreSQL 15 database
- **redis**: Redis for caching and background tasks
- **backend**: FastAPI application server
- **nginx**: Reverse proxy and static file server
- **worker**: Celery background task worker (production only)
- **scheduler**: Celery beat scheduler (production only)

### Network Architecture
```
Internet → Nginx (80/443) → Backend (8000) → Database (5432)
                          → Redis (6379)
```

## 🔧 Configuration

### Environment Files
- `.env` - Development configuration
- `.env.production` - Production configuration (create from example)

### Key Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db
POSTGRES_DB=fado_crm
POSTGRES_USER=fado_user
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=redis_password

# Application
SECRET_KEY=your_jwt_secret_key
ENVIRONMENT=production
STORAGE_DRIVER=local|s3|minio

# External Services
VNPAY_TMN_CODE=your_terminal_code
VNPAY_HASH_SECRET=your_hash_secret
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email
SMTP_PASSWORD=your_app_password
```

## 🚀 Deployment Commands

### Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild services
docker-compose build --no-cache
docker-compose up -d
```

### Production
```bash
# Full deployment
./scripts/deploy.sh deploy

# Health check
./scripts/deploy.sh health

# Rollback
./scripts/deploy.sh rollback

# Manual production start
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring

### Health Checks
- Backend: `http://localhost/health`
- Frontend: `http://localhost/`
- Database: Internal PostgreSQL health check
- Redis: Internal Redis health check

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f nginx

# Production logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Container Status
```bash
# Check running containers
docker-compose ps

# Check container health
docker-compose exec backend python -c "
import requests
response = requests.get('http://localhost:8000/health')
print(f'Health: {response.json()}')
"
```

## 🔒 Security

### Production Security Features
- Non-root user in containers
- Security headers via Nginx
- SSL/TLS termination at Nginx
- Resource limits for containers
- Secret management via environment variables
- Database connection encryption

### SSL Configuration
```bash
# Create SSL directory
mkdir -p ssl

# Copy your SSL certificates
cp your-domain.crt ssl/
cp your-domain.key ssl/

# Update nginx/prod.conf with certificate paths
```

## 📁 Volume Management

### Development Volumes
- `postgres_data`: Database files
- `redis_data`: Redis persistence
- `./uploads`: File uploads (mounted to host)
- `./logs`: Application logs (mounted to host)

### Production Volumes
- `postgres_data`: Database files (Docker volume)
- `redis_data`: Redis persistence (Docker volume)
- `uploads_data`: File uploads (Docker volume)
- `logs_data`: Application logs (Docker volume)

### Backup Volumes
```bash
# Backup database
docker-compose exec postgres pg_dump -U fado_user fado_crm > backup.sql

# Backup uploads
docker cp $(docker-compose ps -q backend):/app/uploads ./uploads-backup

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U fado_user -d fado_crm
```

## 🔧 Troubleshooting

### Common Issues

#### Services not starting
```bash
# Check logs
docker-compose logs

# Check Docker daemon
sudo systemctl status docker

# Check disk space
df -h
```

#### Database connection issues
```bash
# Check database logs
docker-compose logs postgres

# Test database connection
docker-compose exec backend python -c "
from backend.database import engine
try:
    with engine.connect() as conn:
        print('Database connection successful')
except Exception as e:
    print(f'Database error: {e}')
"
```

#### Permission issues
```bash
# Fix upload directory permissions
sudo chown -R $USER:$USER uploads logs

# Fix script permissions
chmod +x scripts/*.sh
```

### Performance Tuning

#### Database Optimization
```sql
-- Connect to database
docker-compose exec postgres psql -U fado_user -d fado_crm

-- Check database performance
EXPLAIN ANALYZE SELECT * FROM khach_hang LIMIT 10;

-- Add indexes (already included in models)
CREATE INDEX IF NOT EXISTS idx_khach_hang_email ON khach_hang(email);
CREATE INDEX IF NOT EXISTS idx_don_hang_trang_thai ON don_hang(trang_thai);
```

#### Container Resources
```yaml
# In docker-compose.prod.yml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '1.0'
    reservations:
      memory: 512M
      cpus: '0.5'
```

## 📞 Support

### Useful Commands
```bash
# Enter container shell
docker-compose exec backend bash
docker-compose exec postgres psql -U fado_user -d fado_crm

# View real-time resource usage
docker stats

# Clean up Docker system
docker system prune -f
docker volume prune -f
```

### Emergency Procedures
```bash
# Emergency stop all services
docker-compose down --timeout 10

# Force restart all services
docker-compose down --timeout 30
docker-compose up -d

# Complete reset (⚠️ DATA LOSS)
docker-compose down -v
docker system prune -af
```

---

## 🎯 Next Steps

After successful Docker deployment:

1. **SSL Setup**: Configure SSL certificates for HTTPS
2. **Domain Setup**: Point your domain to the server
3. **Monitoring**: Setup monitoring with Prometheus/Grafana
4. **Backups**: Configure automated database backups
5. **CI/CD**: Setup GitHub Actions for automated deployments

For production deployment checklist, see `PRODUCTION-CHECKLIST.md`