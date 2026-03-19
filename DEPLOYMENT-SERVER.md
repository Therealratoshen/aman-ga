# 🚀 Deployment Guide - Simple Application Server (Alibaba Cloud)

## 📋 Overview

This guide shows how to deploy Aman ga? v2.1 to a **Simple Application Server** (like Alibaba Cloud ECS) with the existing setup at `http://147.139.202.129`.

---

## 🎯 Deployment Options

### Option 1: Direct Deployment (Current Setup) ⭐ Recommended
- Deploy backend + frontend on same server
- Use Nginx to serve both
- Single IP address

### Option 2: Docker Deployment
- Containerized deployment
- Easy to scale
- Requires Docker knowledge

### Option 3: Separate Frontend/Backend
- Backend on app server
- Frontend on Vercel/Netlify
- Requires CORS configuration

---

## 📦 Option 1: Direct Deployment (Step-by-Step)

### Prerequisites

```bash
# Server requirements
- OS: Ubuntu 20.04+ / CentOS 7+
- RAM: 2GB minimum (4GB recommended)
- Storage: 10GB free space
- Python: 3.10+
- Node.js: 18+ (optional, for build)
```

### Step 1: Connect to Server

```bash
# SSH into your server
ssh root@147.139.202.129

# Or with key
ssh -i ~/.ssh/your_key.pem root@147.139.202.129
```

### Step 2: Install System Dependencies

```bash
# For Ubuntu/Debian
sudo apt update
sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Install Tesseract OCR
sudo apt install -y tesseract-ocr tesseract-ocr-ind libmagic1

# Install Nginx
sudo apt install -y nginx

# For CentOS/RHEL
sudo yum update -y
sudo yum install -y python3 python3-pip tesseract tesseract-langpack-eng libmagic nginx
```

### Step 3: Clone Repository

```bash
# Go to web directory
cd /var/www

# Clone repository
git clone https://github.com/Therealratoshen/aman-ga.git

# Or upload existing code
# Use SCP or FTP to upload files
```

### Step 4: Setup Python Environment

```bash
cd /var/www/aman-ga/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 5: Configure Environment

```bash
# Create .env file
nano .env

# Add configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SECRET_KEY=your-secret-key-change-this
MOCK_MODE=False  # Set to True for testing without Supabase
```

### Step 6: Setup Database (Supabase)

```bash
# 1. Go to https://supabase.com
# 2. Create new project
# 3. Go to SQL Editor
# 4. Run database/schema.sql

# Or use Mock Mode for testing (no database needed)
# Set MOCK_MODE=True in .env
```

### Step 7: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/aman-ga

# Add configuration (see below)
```

**Nginx Configuration:**

```nginx
server {
    listen 80;
    server_name 147.139.202.129;
    
    # Frontend (static files)
    location / {
        root /var/www/aman-ga/frontend/public;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Security headers
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }
    
    # Backend API proxy
    location /token {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /register {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /payment {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase max upload size
        client_max_body_size 20M;
    }
    
    location /admin {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /feedback {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /service {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /validation {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /receipt-formats {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # API documentation
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /openapi.json {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Step 8: Enable Nginx Configuration

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/aman-ga /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### Step 9: Setup Systemd Service for Backend

```bash
# Create service file
sudo nano /etc/systemd/system/aman-ga.service

# Add configuration
[Unit]
Description=Aman ga? Backend API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/aman-ga/backend
Environment="PATH=/var/www/aman-ga/backend/venv/bin"
ExecStart=/var/www/aman-ga/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 10: Start Backend Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable aman-ga

# Start service
sudo systemctl start aman-ga

# Check status
sudo systemctl status aman-ga

# View logs
sudo journalctl -u aman-ga -f
```

### Step 11: Configure Firewall

```bash
# For UFW (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# For firewalld (CentOS)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### Step 12: Test Deployment

```bash
# Test backend
curl http://147.139.202.129/health

# Test frontend
curl http://147.139.202.129/

# Test API documentation
curl http://147.139.202.129/docs
```

**Expected Results:**
- `http://147.139.202.129/` → Shows modern UI
- `http://147.139.202.129/health` → `{"status": "healthy"}`
- `http://147.139.202.129/docs` → Swagger UI

---

## 🐳 Option 2: Docker Deployment

### Step 1: Create Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ind \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Create docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - MOCK_MODE=${MOCK_MODE:-False}
    volumes:
      - ./backend:/app
      - ocr_config:/app/ocr_config
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./frontend/public:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  ocr_config:
```

### Step 3: Create Nginx Config for Docker

```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /token {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Step 4: Build and Run

```bash
# Build and start containers
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Stop containers
docker-compose down
```

---

## 📊 Option 3: Hybrid (Backend on Server, Frontend on Vercel)

### Step 1: Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Go to frontend directory
cd aman-ga/frontend/public

# Deploy
vercel --prod
```

### Step 2: Update Backend CORS

```python
# In backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",  # Vercel URL
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 3: Configure Environment Variables on Vercel

```
NEXT_PUBLIC_API_URL=https://147.139.202.129
```

---

## 🔒 SSL/HTTPS Setup (Recommended)

### Using Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

### Update Nginx for HTTPS

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # ... rest of configuration
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 🔧 Maintenance Commands

### Check Service Status

```bash
# Backend service
sudo systemctl status aman-ga

# Nginx
sudo systemctl status nginx

# View logs
sudo journalctl -u aman-ga -f
sudo tail -f /var/log/nginx/error.log
```

### Restart Services

```bash
# Restart backend
sudo systemctl restart aman-ga

# Restart Nginx
sudo systemctl restart nginx

# Restart both
sudo systemctl restart aman-ga nginx
```

### Update Application

```bash
# Go to app directory
cd /var/www/aman-ga

# Pull latest changes
git pull

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install -r backend/requirements.txt

# Restart service
sudo systemctl restart aman-ga
```

### Backup Data

```bash
# Backup OCR configuration
tar -czf ocr_config_backup.tar.gz /var/www/aman-ga/backend/ocr_config/

# Backup database (if using Supabase, it's cloud-hosted)
# Download backup from Supabase dashboard
```

---

## 📈 Performance Optimization

### 1. Enable Gzip Compression

```nginx
# In nginx.conf
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript 
           application/x-javascript application/xml+rss 
           application/json application/javascript;
```

### 2. Set Up Caching

```nginx
# In nginx.conf
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. Increase Worker Processes

```nginx
# In /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 1024;
```

---

## 🚨 Troubleshooting

### Backend Not Starting

```bash
# Check logs
sudo journalctl -u aman-ga -f

# Common issues:
# - Port 8000 already in use
# - Missing dependencies
# - Wrong Python path

# Fix port conflict
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Nginx Errors

```bash
# Test configuration
sudo nginx -t

# Check error log
sudo tail -f /var/log/nginx/error.log

# Common issues:
# - Syntax error in config
# - Permission denied
# - Upstream not available
```

### OCR Not Working

```bash
# Check Tesseract installation
tesseract --version

# Check language data
tesseract --list-langs

# Install if missing
sudo apt install tesseract-ocr-ind
```

### Permission Issues

```bash
# Set correct permissions
sudo chown -R www-data:www-data /var/www/aman-ga/frontend/public
sudo chmod -R 755 /var/www/aman-ga
```

---

## 📊 Monitoring Setup

### Install Monitoring Tools

```bash
# Install htop for system monitoring
sudo apt install -y htop

# Install netdata for real-time monitoring
bash <(curl -Ss https://my-netdata.io/kickstart.sh)
```

### Set Up Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/aman-ga

# Add configuration
/var/log/aman-ga/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    postrotate
        systemctl reload aman-ga
    endscript
}
```

---

## ✅ Deployment Checklist

- [ ] System dependencies installed
- [ ] Python virtual environment created
- [ ] Requirements installed
- [ ] .env file configured
- [ ] Database setup (or Mock Mode enabled)
- [ ] Nginx configured
- [ ] Systemd service created
- [ ] Firewall configured
- [ ] SSL certificate installed (optional)
- [ ] Health endpoint responds
- [ ] Frontend loads correctly
- [ ] File upload works
- [ ] OCR functionality tested
- [ ] Feedback system tested
- [ ] Backup strategy in place
- [ ] Monitoring configured

---

## 🎯 Quick Deploy Script

Save as `deploy.sh`:

```bash
#!/bin/bash

set -e

echo "🚀 Deploying Aman ga? v2.1..."

# Install dependencies
echo "📦 Installing dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv tesseract-ocr tesseract-ocr-ind libmagic1 nginx

# Setup Python
echo "🐍 Setting up Python..."
cd /var/www/aman-ga/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup Nginx
echo "🌐 Configuring Nginx..."
sudo cp /var/www/aman-ga/nginx.conf /etc/nginx/sites-available/aman-ga
sudo ln -sf /etc/nginx/sites-available/aman-ga /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Setup Service
echo "🔧 Setting up systemd service..."
sudo cp /var/www/aman-ga/aman-ga.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aman-ga
sudo systemctl start aman-ga

echo "✅ Deployment complete!"
echo "🌐 Access at: http://$(hostname -I | awk '{print $1}')"
```

Run:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

**Version**: 2.1.0  
**Last Updated**: March 19, 2026  
**Tested On**: Ubuntu 20.04, CentOS 7, Alibaba Cloud ECS
