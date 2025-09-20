# Jersey Artwork Production Deployment Guide

## Overview
This guide covers deploying the Jersey Artwork platform to Digital Ocean App Platform with full production security hardening.

## Pre-Deployment Checklist

### 1. Security Requirements
- [ ] Generate strong SECRET_KEY (minimum 50 characters)
- [ ] Configure all environment variables from `.env.production.example`
- [ ] Set up SSL certificates (handled by Digital Ocean)
- [ ] Configure domain DNS records
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy

### 2. Digital Ocean Resources
- [ ] Create Digital Ocean account
- [ ] Set up Managed PostgreSQL database
- [ ] Set up Managed Redis instance
- [ ] Create Spaces bucket for static/media files
- [ ] Configure CDN for Spaces (optional but recommended)

### 3. Third-Party Services
- [ ] SumUp merchant account and API credentials
- [ ] Google Workspace email account with app-specific password
- [ ] Google reCAPTCHA keys
- [ ] Sentry account for error tracking

## Deployment Steps

### Step 1: Prepare Repository
```bash
# Ensure all changes are committed
git add .
git commit -m "Production deployment configuration"

# Push to GitHub
git push origin main
```

### Step 2: Create Digital Ocean Resources

#### Database
1. Go to Digital Ocean Control Panel
2. Create Database > PostgreSQL
3. Choose region (same as app)
4. Select "Professional" plan or higher for production
5. Note the connection string

#### Redis Cache
1. Create Database > Redis
2. Choose same region as app
3. Select appropriate plan
4. Note the connection string

#### Spaces (Object Storage)
1. Create Spaces bucket
2. Name: `jersey-artwork`
3. Region: Choose closest to users
4. Create Spaces access keys
5. Configure CORS if needed

### Step 3: Deploy Application

#### Using Digital Ocean CLI
```bash
# Install doctl
brew install doctl  # macOS
# or
snap install doctl  # Linux

# Authenticate
doctl auth init

# Update app.yaml with your GitHub repository
sed -i 's/YOUR_GITHUB_USERNAME/your-actual-username/g' app.yaml

# Create app
doctl apps create --spec app.yaml

# Get app ID
doctl apps list

# Monitor deployment
doctl apps logs YOUR_APP_ID --follow
```

#### Using Web Interface
1. Go to Apps in Digital Ocean Control Panel
2. Click "Create App"
3. Connect GitHub repository
4. Choose branch (main)
5. Configure environment variables
6. Deploy

### Step 4: Post-Deployment Configuration

#### Run Database Migrations
```bash
# Connect to app console
doctl apps console YOUR_APP_ID web

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files (if not in build)
python manage.py collectstatic --noinput
```

#### Configure Domain
1. Add custom domain in App settings
2. Update DNS records:
   - A record: @ -> Digital Ocean App IP
   - CNAME: www -> @ or app URL
3. Enable Force HTTPS

#### Test Security Headers
```bash
# Check security headers
curl -I https://your-domain.com

# Should see:
# - Strict-Transport-Security
# - X-Content-Type-Options: nosniff
# - X-Frame-Options: DENY
# - X-XSS-Protection: 1; mode=block
```

## Production Monitoring

### 1. Application Monitoring
- Set up Sentry alerts for errors
- Configure Digital Ocean monitoring
- Set up uptime monitoring (e.g., UptimeRobot)

### 2. Security Monitoring
```bash
# Check for security updates regularly
pip list --outdated

# Run security audit
pip-audit

# Django security check
python manage.py check --deploy
```

### 3. Database Monitoring
- Enable slow query logs
- Set up backup schedule
- Monitor connection pool usage

### 4. Performance Monitoring
- Monitor response times
- Track database query performance
- Monitor static asset loading

## Backup Strategy

### Database Backups
```bash
# Manual backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup_20240101.sql
```

### Media Files Backup
- Configure Spaces versioning
- Set up lifecycle rules for old versions
- Regular exports to separate bucket

## Security Best Practices

### 1. Regular Updates
```bash
# Weekly security updates
pip install --upgrade $(pip list --outdated | awk 'NR>2 {print $1}')

# Test after updates
python manage.py test

# Deploy if tests pass
git push origin main
```

### 2. Access Control
- Use SSH keys for server access
- Enable 2FA on all services
- Rotate API keys quarterly
- Review user permissions monthly

### 3. Incident Response
1. Have incident response plan
2. Document security contacts
3. Test restore procedures
4. Keep audit logs

## Troubleshooting

### Common Issues

#### Static Files Not Loading
```bash
# Verify static files collected
python manage.py collectstatic --noinput

# Check Spaces permissions
# Ensure bucket is public-read for static files
```

#### Database Connection Issues
```bash
# Test connection
python manage.py dbshell

# Check SSL requirement
# Ensure sslmode=require in DATABASE_URL
```

#### Email Not Sending
```bash
# Test email configuration
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

#### High Memory Usage
```bash
# Check worker count
# Reduce if necessary in app.yaml

# Monitor with
doctl apps metrics get YOUR_APP_ID
```

## Scaling Guidelines

### When to Scale
- Response time > 1 second consistently
- CPU usage > 80% sustained
- Memory usage > 90%
- Database connections maxed out

### How to Scale
1. **Horizontal Scaling**: Increase instance count
2. **Vertical Scaling**: Upgrade instance size
3. **Database Scaling**: Upgrade database plan
4. **Caching**: Implement aggressive caching

## Maintenance Mode

### Enable Maintenance Mode
```python
# Add to settings_production.py
MAINTENANCE_MODE = os.environ.get('MAINTENANCE_MODE', 'False') == 'True'

# Add middleware to handle
if MAINTENANCE_MODE:
    return HttpResponse('Site under maintenance', status=503)
```

### Scheduled Maintenance
1. Announce 24 hours in advance
2. Enable maintenance mode
3. Perform updates
4. Test thoroughly
5. Disable maintenance mode

## Support Contacts

- Digital Ocean Support: support.digitalocean.com
- Payment Gateway Support: [Provider specific]
- Domain Registrar: [Your registrar]
- Email Provider: Google Workspace support

## Compliance

### GDPR Compliance
- Privacy policy implemented
- Cookie consent banner
- Data export functionality
- Right to deletion process

### PCI Compliance
- Never store card details
- Use payment gateway tokens only
- SSL/TLS enforced
- Regular security audits

## Performance Optimization

### Database Optimization
```python
# Add database indexes
python manage.py makemigrations --empty yourapp
# Add index definitions

# Optimize queries
python manage.py shell_plus --print-sql
```

### Caching Strategy
- Page caching for static content
- Query caching for expensive operations
- CDN for static assets
- Browser caching headers

## Rollback Procedure

If deployment fails:
1. Revert to previous app version in Digital Ocean
2. Restore database from backup if schema changed
3. Clear cache
4. Notify users if service affected

## Health Checks

The application includes health check endpoint at `/health/`
- Checks database connectivity
- Checks cache connectivity
- Returns JSON status

Monitor with:
```bash
curl https://your-domain.com/health/
```

## Final Checklist

Before going live:
- [ ] All tests passing
- [ ] Security scan completed
- [ ] SSL certificate active
- [ ] Monitoring configured
- [ ] Backups tested
- [ ] Error tracking active
- [ ] Admin account created
- [ ] Payment gateway tested
- [ ] Email sending verified
- [ ] Load testing completed

## Notes

- Keep this document updated with any changes
- Document all incidents and resolutions
- Review security quarterly
- Test disaster recovery annually