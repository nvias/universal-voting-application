# NVIAS Voting System - Portainer Deployment Guide with Traefik

## 🚨 **Fixing the Volume Mount Error**

The error you encountered:
```
failed to populate volume: error while mounting volume '/var/lib/docker/volumes/nvias_voting_postgres_data_prod/_data': failed to mount local volume: mount /data/compose/53/data/postgres:/var/lib/docker/volumes/nvias_voting_postgres_data_prod/_data, flags: 0x1000: no such file or directory
```

This happens because the previous Docker Compose configuration used **bind mounts** that reference local file paths that don't exist in your Portainer environment.

## ✅ **Solution: Updated Configuration with Traefik + Docker Managed Volumes**

I've created a Portainer-specific configuration that:
- ✅ Uses **Docker managed volumes** instead of bind mounts
- ✅ Includes **Traefik** configuration for reverse proxy and SSL
- ✅ Compatible with Portainer's deployment system
- ✅ Maintains all original functionality

## 🚀 **Deployment Steps in Portainer**

### **Step 1: Ensure Traefik Network Exists**

Before deploying, make sure the `traefik_proxy` network exists:

1. In Portainer, go to **Networks**
2. Check if `traefik_proxy` network exists
3. If not, create it:
   - Click **Add network**
   - Name: `traefik_proxy`
   - Driver: `bridge`
   - Click **Create network**

### **Step 2: Stop Current Stack (if running)**
In Portainer:
1. Go to **Stacks**
2. Find your `nvias-voting` stack
3. Click **Stop** and then **Remove**

### **Step 3: Create New Stack with Traefik Configuration**

1. In Portainer, go to **Stacks** → **Add Stack**
2. Name it: `nvias-voting`
3. Use the **Web editor** option
4. Copy and paste the contents of `docker-compose.portainer.yml`

### **Step 4: Configure Environment Variables**

In the **Environment variables** section, add these variables:

**Required Variables:**
```env
COMPOSE_PROJECT_NAME=nvias-voting
WEB_DOMAIN=voting.yourdomain.com
APP_URL=https://voting.yourdomain.com
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-change-this
POSTGRES_DB=voting_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_production_password
CERT_RESOLVER=main-resolver
CORS_ORIGINS=https://voting.yourdomain.com
```

**Optional Variables (for pgAdmin):**
```env
PGADMIN_ENABLE=true
PGADMIN_DOMAIN=pgadmin.yourdomain.com
PGADMIN_EMAIL=admin@yourdomain.com
PGADMIN_PASSWORD=admin_secure_password
```

**⚠️ Important:** 
- Replace `yourdomain.com` with your actual domain
- Change all passwords to secure values
- Make sure `CERT_RESOLVER` matches your Traefik certificate resolver name

### **Step 5: Deploy Stack**

1. Click **Deploy the stack**
2. Wait for deployment to complete
3. Check **Containers** section to verify both containers are running

## 🌐 **Access Your Application**

After successful deployment:

- **Main Application**: `https://voting.yourdomain.com`
- **Admin Interface**: `https://voting.yourdomain.com`
- **API Health Check**: `https://voting.yourdomain.com/api/v1/health`
- **pgAdmin** (if enabled): `https://pgadmin.yourdomain.com`

## 🔍 **Verify Deployment**

### **1. Check Container Status**
In Portainer → **Containers**:
- `nvias-voting-db-1` should be **running** and **healthy**
- `nvias-voting-voting-app-1` should be **running** and **healthy**

### **2. Check Traefik Routes**
If you have Traefik dashboard:
- Verify the routes are showing up
- Check SSL certificates are being generated

### **3. Test Application**
```bash
# Test health endpoint
curl -k https://voting.yourdomain.com/api/v1/health

# Should return: {"status":"healthy","timestamp":"...","version":"1.0"}
```

### **4. Initialize Database**
In Portainer → **Containers** → `nvias-voting-voting-app-1` → **Console**:
```bash
python init_db.py
```

You should see:
```
Creating database tables...
Added template: Rating Scale 1-5
Added template: Yes/No Question
Added template: Multiple Choice
Added template: Team Selection
Database initialized successfully!
```

## 🔧 **Traefik Configuration Requirements**

### **Prerequisites:**
1. **Traefik** must be running and accessible
2. **traefik_proxy** network must exist
3. **Certificate resolver** configured in Traefik
4. **DNS** pointing to your server

### **Traefik Labels Explained:**
```yaml
# Enable Traefik for this service
- "traefik.enable=true"
- "traefik.docker.network=traefik_proxy"

# HTTP (redirects to HTTPS)
- "traefik.http.routers.web_nvias-voting.entrypoints=web"
- "traefik.http.routers.web_nvias-voting.rule=Host(`voting.yourdomain.com`)"
- "traefik.http.routers.web_nvias-voting.middlewares=web_nvias-voting_https"
- "traefik.http.middlewares.web_nvias-voting_https.redirectscheme.scheme=https"

# HTTPS with SSL certificate
- "traefik.http.routers.web_nvias-voting-https.entrypoints=websecure"
- "traefik.http.routers.web_nvias-voting-https.rule=Host(`voting.yourdomain.com`)"
- "traefik.http.routers.web_nvias-voting-https.tls=true"
- "traefik.http.routers.web_nvias-voting-https.tls.certresolver=main-resolver"
- "traefik.http.services.web_nvias-voting-https.loadbalancer.server.port=5000"
```

## 💾 **Database Management with Docker Volumes**

### **Volume Benefits:**
- ✅ **Automatic management** by Docker/Portainer
- ✅ **Persistent** across container restarts
- ✅ **No path dependencies** - works anywhere
- ✅ **Backup friendly** - can be backed up as volumes
- ✅ **Performance optimized** for container storage

### **Volume Locations:**
```yaml
volumes:
  postgres_data_portainer:     # PostgreSQL data
  app_data_portainer:          # Application data
  backup_data_portainer:       # Backup files
  logs_data_portainer:         # Application logs
  pgadmin_data_portainer:      # pgAdmin configuration
```

### **Create Manual Backup:**
```bash
# Access the voting-app container console in Portainer
mkdir -p /app/backups
pg_dump -h db -U postgres -d voting_db --clean --create > /app/backups/manual_backup_$(date +%Y%m%d_%H%M%S).sql
```

### **List Backups:**
```bash
# In voting-app container console
ls -la /app/backups/
```

### **Restore Backup:**
```bash
# In voting-app container console
psql -h db -U postgres -d postgres < /app/backups/your_backup_file.sql
```

## 🔐 **Security Considerations**

### **Environment Variables Security:**
```env
# Use strong passwords
POSTGRES_PASSWORD=ComplexPassword123!@#
SECRET_KEY=very-long-random-string-min-32-chars
PGADMIN_PASSWORD=AnotherStrongPassword456$%^

# Restrict CORS for production
CORS_ORIGINS=https://voting.yourdomain.com

# Use HTTPS URLs
APP_URL=https://voting.yourdomain.com
```

### **Network Security:**
- Application only accessible through Traefik (HTTPS)
- Database not exposed to external networks
- Internal communication on `local` network

## 🚨 **Troubleshooting**

### **Stack Won't Deploy:**
1. **Check Traefik network**: Ensure `traefik_proxy` network exists
2. **Verify environment variables**: All required variables set
3. **Check domain DNS**: Domain points to your server
4. **Review Portainer logs**: Check deployment logs for errors

### **Containers Start but Application Not Accessible:**
1. **Check Traefik**: Ensure Traefik is running and configured
2. **Verify DNS**: Domain resolves to correct IP
3. **Check certificate resolver**: Traefik can generate SSL certificates
4. **Review Traefik logs**: Look for routing errors

### **Database Connection Issues:**
```bash
# Test from voting-app container
ping db
telnet db 5432

# Check database logs
# In db container console
tail -f /var/log/postgresql/postgresql-*.log
```

### **SSL Certificate Issues:**
1. **Verify certificate resolver** name in Traefik config
2. **Check DNS propagation** for your domain
3. **Review Traefik certificate logs**
4. **Ensure ports 80/443** are accessible from internet

## 📊 **Monitoring in Production**

### **Health Checks:**
```bash
# API health
curl -k https://voting.yourdomain.com/api/v1/health

# Database health (from voting-app container)
pg_isready -h db -U postgres -d voting_db
```

### **Container Resource Usage:**
Monitor in Portainer → **Containers** → Select container → **Stats**

### **Log Monitoring:**
- **Application logs**: Portainer → Container → **Logs**
- **Database logs**: Access db container console and check PostgreSQL logs
- **Traefik logs**: Check Traefik container logs for routing issues

## 🔄 **Updates and Maintenance**

### **Update Application:**
1. In Portainer → **Stacks** → `nvias-voting`
2. Click **Editor**
3. Update image tags or configuration
4. Click **Update the stack**

### **Backup Before Updates:**
```bash
# Always create backup before updates
python3 backup_portainer.py --backup --stack nvias-voting
```

### **Database Maintenance:**
```bash
# In db container console
# Analyze and vacuum database
psql -U postgres -d voting_db -c "VACUUM ANALYZE;"

# Check database size
psql -U postgres -d voting_db -c "SELECT pg_size_pretty(pg_database_size('voting_db'));"
```

## ✅ **Success Indicators**

After successful deployment:

1. ✅ **Containers running**: Both db and voting-app containers show "running" and "healthy"
2. ✅ **HTTPS accessible**: `https://voting.yourdomain.com` loads the admin interface
3. ✅ **SSL certificate**: Browser shows secure connection (padlock icon)
4. ✅ **API responding**: `/api/v1/health` returns healthy status
5. ✅ **Database initialized**: Can create voting sessions in admin interface
6. ✅ **Traefik routing**: Routes visible in Traefik dashboard (if available)

Your NVIAS Voting System is now successfully deployed with Traefik, Docker managed volumes, and production-ready configuration! 🚀
