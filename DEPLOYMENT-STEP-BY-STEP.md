# 🚀 Step-by-Step Deployment Guide

## Quick Overview

This guide will help you deploy **Aman ga? v2.1** to a **Simple Application Server** (Alibaba Cloud, DigitalOcean, Linode, etc.) in **10 easy steps**.

**Time Required:** 15-20 minutes  
**Difficulty:** ⭐⭐☆☆☆ (Easy)  
**Cost:** ~$5-10/month

---

## 📋 Prerequisites

### What You Need

1. **A VPS server** (Virtual Private Server)
   - Alibaba Cloud Simple Application Server
   - DigitalOcean Droplet
   - Linode/Cloud
   - AWS Lightsail
   - Any VPS with root access

2. **Server Requirements**
   ```
   OS: Ubuntu 20.04 or 22.04 (recommended)
   RAM: 2GB minimum (4GB recommended)
   Storage: 20GB+ SSD
   Python: 3.10+ (we'll install it)
   ```

3. **SSH Access** to your server
4. **Domain name** (optional - can use IP address)

---

## 🎯 Step-by-Step Instructions

### Step 1: Connect to Your Server

Open your terminal and SSH into your server:

```bash
# Replace with your server IP
ssh root@YOUR_SERVER_IP

# If using SSH key
ssh -i ~/.ssh/your_key.pem root@YOUR_SERVER_IP
```

**Example:**
```bash
ssh root@147.139.202.129
```

You should see something like:
```
Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.4.0-150-generic x86_64)
root@your-server:~#
```

---

### Step 2: Update System Packages

```bash
# Update package list
apt update

# Upgrade installed packages
apt upgrade -y
```

This ensures you have the latest security patches.

---

### Step 3: Install Required Software

```bash
# Install Python and tools
apt install -y python3 python3-pip python3-venv

# Install Tesseract OCR (for receipt scanning)
apt install -y tesseract-ocr tesseract-ocr-ind libmagic1

# Install Nginx (web server)
apt install -y nginx

# Install Git (to clone the repo)
apt install -y git

# Install curl (for testing)
apt install -y curl
```

**Verify installations:**
```bash
python3 --version  # Should show Python 3.10+
tesseract --version  # Should show Tesseract version
nginx -v  # Should show Nginx version
```

---

### Step 4: Clone the Repository

```bash
# Create web directory
mkdir -p /var/www
cd /var/www

# Clone the repository
git clone https://github.com/Therealratoshen/aman-ga.git

# Enter the directory
cd aman-ga
```

---

### Step 5: Setup Python Virtual Environment

```bash
# Go to backend directory
cd /var/www/aman-ga/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

**Note:** This may take 5-10 minutes to install all packages.

---

### Step 6: Configure Environment

```bash
# Create .env file
nano .env
```

**Add this configuration:**

```env
# Application Settings
APP_NAME=Aman ga?
DEBUG=False

# JWT Settings (generate a new secret key!)
SECRET_KEY=your-super-secret-key-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Settings
# For demo/testing, use Mock Mode (no database needed)
MOCK_MODE=True

# For production with Supabase:
# MOCK_MODE=False
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your-anon-key
```

**To generate a SECRET_KEY:**
```bash
# In a new terminal (not the nano editor)
openssl rand -hex 32
```

Copy the output and paste it in the `.env` file.

**Save and exit nano:**
- Press `Ctrl + O` then `Enter` (save)
- Press `Ctrl + X` (exit)

---

### Step 7: Setup Nginx Web Server

```bash
# Copy the nginx configuration file
cp /var/www/aman-ga/nginx.conf /etc/nginx/sites-available/aman-ga

# Enable the site
ln -s /etc/nginx/sites-available/aman-ga /etc/nginx/sites-enabled/

# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t
```

If you see `syntax is ok` and `test is successful`, continue:

```bash
# Restart Nginx
systemctl restart nginx

# Enable Nginx to start on boot
systemctl enable nginx
```

---

### Step 8: Setup Backend Service (Systemd)

```bash
# Copy the service file
cp /var/www/aman-ga/aman-ga.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable service to start on boot
systemctl enable aman-ga

# Start the service
systemctl start aman-ga

# Check status
systemctl status aman-ga
```

You should see `active (running)` in green.

Press `q` to exit the status view.

---

### Step 9: Configure Firewall

```bash
# If UFW is installed
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS (for later)
ufw allow 22/tcp    # SSH
ufw enable

# If firewalld is installed
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-service=ssh
firewall-cmd --reload
```

---

### Step 10: Test Your Deployment

```bash
# Test backend health
curl http://localhost/health

# Should return: {"status":"healthy","version":"2.1.0",...}

# Test frontend
curl http://localhost/

# Should return HTML content
```

**Open your browser and visit:**
```
http://YOUR_SERVER_IP/
```

**You should see the Aman ga? homepage!**

---

## ✅ Verification Checklist

### Backend Checks
```bash
# Check if backend is running
systemctl status aman-ga

# Should show: active (running)

# Check backend logs
journalctl -u aman-ga -f

# Test API endpoint
curl http://localhost/health
```

### Frontend Checks
```bash
# Check if Nginx is running
systemctl status nginx

# Should show: active (running)

# Test frontend
curl http://localhost/ | head -20
```

### Access Checks
- [ ] Can access `http://YOUR_SERVER_IP/` in browser
- [ ] Can login with demo credentials
- [ ] Can upload a test image
- [ ] OCR extraction works
- [ ] Admin dashboard accessible

---

## 🔧 Common Issues & Solutions

### Issue 1: "Port 8000 already in use"

**Problem:** Another service is using port 8000

**Solution:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Restart aman-ga
systemctl restart aman-ga
```

### Issue 2: "502 Bad Gateway"

**Problem:** Backend is not running

**Solution:**
```bash
# Check backend status
systemctl status aman-ga

# Restart backend
systemctl restart aman-ga

# Check logs for errors
journalctl -u aman-ga -f
```

### Issue 3: "404 Not Found"

**Problem:** Nginx configuration issue

**Solution:**
```bash
# Test Nginx config
nginx -t

# Reload Nginx
systemctl reload nginx

# Check Nginx error log
tail -f /var/log/nginx/error.log
```

### Issue 4: "OCR not working"

**Problem:** Tesseract not installed correctly

**Solution:**
```bash
# Check Tesseract installation
tesseract --version

# Reinstall if needed
apt install -y tesseract-ocr tesseract-ocr-ind

# Test OCR
cd /var/www/aman-ga/backend
python3 -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

### Issue 5: "Permission denied" errors

**Problem:** File permissions incorrect

**Solution:**
```bash
# Fix ownership
chown -R www-data:www-data /var/www/aman-ga/frontend/public

# Fix permissions
chmod -R 755 /var/www/aman-ga
```

---

## 📊 Post-Deployment Tasks

### 1. Change Default Passwords

**Edit the database or use the admin panel to change:**
- Admin password (`admin@amanga.id`)
- Finance password (`finance@amanga.id`)

### 2. Setup SSL/HTTPS (Recommended)

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Get SSL certificate (if you have a domain)
certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

### 3. Setup Monitoring

```bash
# Install htop for system monitoring
apt install -y htop

# Check system resources
htop

# Monitor logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 4. Setup Backups

```bash
# Create backup script
nano /usr/local/bin/backup-aman-ga.sh
```

**Add:**
```bash
#!/bin/bash
BACKUP_DIR="/backups/aman-ga"
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/backup-$(date +%Y%m%d).tar.gz /var/www/aman-ga/backend/ocr_config
```

**Make executable:**
```bash
chmod +x /usr/local/bin/backup-aman-ga.sh

# Add to crontab (daily backup)
crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-aman-ga.sh
```

---

## 🔄 Updating Your Deployment

When there's a new version:

```bash
# Go to app directory
cd /var/www/aman-ga

# Pull latest changes
git pull

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Restart service
systemctl restart aman-ga

# Check status
systemctl status aman-ga
```

---

## 📈 Monitoring & Maintenance

### Daily Checks
```bash
# Check service status
systemctl status aman-ga
systemctl status nginx

# Check disk space
df -h

# Check memory
free -h
```

### Weekly Checks
```bash
# View error logs
journalctl -u aman-ga --since "1 week ago"
tail -100 /var/log/nginx/error.log

# Check for updates
apt update
```

### Monthly Checks
```bash
# Apply security updates
apt upgrade -y

# Clean old logs
journalctl --vacuum-time=7d

# Restart services (optional)
systemctl restart aman-ga
systemctl restart nginx
```

---

## 🎯 Quick Reference

### Service Commands
```bash
# Start/Stop/Restart
systemctl start aman-ga
systemctl stop aman-ga
systemctl restart aman-ga

# Check status
systemctl status aman-ga

# View logs
journalctl -u aman-ga -f
```

### Nginx Commands
```bash
# Start/Stop/Restart
systemctl start nginx
systemctl stop nginx
systemctl restart nginx

# Test config
nginx -t

# View logs
tail -f /var/log/nginx/error.log
```

### Useful Commands
```bash
# Check what's running
ps aux | grep python
ps aux | grep nginx

# Check ports
netstat -tulpn | grep :80
netstat -tulpn | grep :8000

# Check disk usage
du -sh /var/www/aman-ga
```

---

## 📞 Getting Help

### Logs
```bash
# Backend logs
journalctl -u aman-ga -f

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# System logs
tail -f /var/log/syslog
```

### Documentation
- **[QUICK-REFERENCE.md](./QUICK-REFERENCE.md)** - Common commands
- **[DEPLOYMENT-SERVER.md](./DEPLOYMENT-SERVER.md)** - Detailed guide
- **[LIVE-DEMO.md](./LIVE-DEMO.md)** - Demo information

### GitHub
- **Issues:** https://github.com/Therealratoshen/aman-ga/issues
- **Discussions:** https://github.com/Therealratoshen/aman-ga/discussions

---

## ✅ Deployment Complete!

**Congratulations!** 🎉

Your Aman ga? application is now live!

**Access Points:**
- **Frontend:** `http://YOUR_SERVER_IP/`
- **API Docs:** `http://YOUR_SERVER_IP/docs`
- **Health Check:** `http://YOUR_SERVER_IP/health`

**Demo Credentials:**
- **Admin:** `admin@amanga.id` / `admin123`
- **Finance:** `finance@amanga.id` / `admin123`

**⚠️ Remember:**
- Change default passwords!
- Setup SSL/HTTPS for production
- This is a demo system - no real payments

---

**Last Updated:** March 19, 2026  
**Version:** 2.1.0  
**Tested On:** Ubuntu 20.04, 22.04
