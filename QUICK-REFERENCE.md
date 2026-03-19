# 📋 Quick Reference Card - Aman ga? v2.1

## 🚀 Deploy to Simple Application Server

### One-Command Deploy

```bash
# SSH to server
ssh root@YOUR_SERVER_IP

# Clone and deploy
git clone https://github.com/Therealratoshen/aman-ga.git
cd aman-ga
sudo ./deploy.sh
```

### Manual Deploy (Step-by-Step)

```bash
# 1. Install dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y tesseract-ocr tesseract-ocr-ind libmagic1
sudo apt install -y nginx

# 2. Setup Python
cd /var/www/aman-ga/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
nano .env  # Edit settings

# 4. Setup Nginx
sudo cp nginx.conf /etc/nginx/sites-available/aman-ga
sudo ln -s /etc/nginx/sites-available/aman-ga /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 5. Setup Service
sudo cp aman-ga.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aman-ga
sudo systemctl start aman-ga

# 6. Test
curl http://YOUR_SERVER_IP/health
```

---

## 🔧 Common Commands

### Service Management

```bash
# Start/Stop/Restart Backend
sudo systemctl start aman-ga
sudo systemctl stop aman-ga
sudo systemctl restart aman-ga

# Check Status
sudo systemctl status aman-ga

# View Logs
sudo journalctl -u aman-ga -f
sudo tail -f /var/log/nginx/error.log

# Enable/Disable on Boot
sudo systemctl enable aman-ga
sudo systemctl disable aman-ga
```

### Nginx Management

```bash
# Restart Nginx
sudo systemctl restart nginx

# Test Configuration
sudo nginx -t

# Reload Config
sudo nginx -s reload
```

### Application Update

```bash
cd /var/www/aman-ga
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart aman-ga
```

---

## 📊 Testing Endpoints

```bash
# Health Check
curl http://YOUR_SERVER_IP/health

# API Documentation
curl http://YOUR_SERVER_IP/docs

# Login Test
curl -X POST http://YOUR_SERVER_IP/token \
  -d "username=admin@amanga.id&password=admin123"

# Upload Test (with token)
curl -X POST http://YOUR_SERVER_IP/payment/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "service_type=CEK_DASAR" \
  -F "amount=1000" \
  -F "payment_method=BANK_TRANSFER" \
  -F "bank_name=BCA" \
  -F "transaction_id=TRX123" \
  -F "transaction_date=2024-03-19T10:00:00" \
  -F "proof_image=@test.jpg"
```

---

## 🔍 Troubleshooting

### Backend Not Running

```bash
# Check status
sudo systemctl status aman-ga

# View logs
sudo journalctl -u aman-ga -f

# Restart
sudo systemctl restart aman-ga

# Check port
sudo lsof -i :8000
```

### Nginx Errors

```bash
# Test config
sudo nginx -t

# View error log
sudo tail -f /var/log/nginx/error.log

# Restart
sudo systemctl restart nginx
```

### OCR Not Working

```bash
# Check Tesseract
tesseract --version

# List languages
tesseract --list-langs

# Install Indonesian
sudo apt install tesseract-ocr-ind
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/aman-ga/frontend/public

# Fix permissions
sudo chmod -R 755 /var/www/aman-ga
```

---

## 📁 File Locations

```
/var/www/aman-ga/              # Application root
/var/www/aman-ga/backend/      # Backend code
/var/www/aman-ga/backend/.env  # Environment config
/var/www/aman-ga/backend/venv/ # Python virtual env
/var/www/aman-ga/frontend/public/ # Frontend files

/etc/nginx/sites-available/aman-ga  # Nginx config
/etc/nginx/sites-enabled/aman-ga    # Nginx enabled
/etc/systemd/system/aman-ga.service # Systemd service

/var/log/nginx/error.log       # Nginx error log
/var/log/nginx/access.log      # Nginx access log
journalctl -u aman-ga          # Backend logs
```

---

## 🔐 Security Checklist

- [ ] Change SECRET_KEY in .env
- [ ] Set MOCK_MODE=False for production
- [ ] Configure Supabase credentials
- [ ] Enable firewall (UFW/firewalld)
- [ ] Install SSL certificate (Certbot)
- [ ] Update admin passwords
- [ ] Enable rate limiting (default: on)
- [ ] Set up regular backups

---

## 📈 Monitoring

```bash
# System resources
htop

# Disk usage
df -h
du -sh /var/www/aman-ga

# Memory usage
free -h

# Network connections
netstat -tulpn

# Process list
ps aux | grep aman-ga
```

---

## 🗄️ Database Setup (Supabase)

1. Go to https://supabase.com
2. Create new project
3. Get URL and anon key
4. Run `database/schema.sql` in SQL Editor
5. Update `.env` with credentials
6. Set `MOCK_MODE=False`

---

## 🎯 Performance Tips

### Enable Gzip (Nginx)

```nginx
# Add to nginx.conf
gzip on;
gzip_vary on;
gzip_types text/plain text/css application/json application/javascript;
```

### Increase Upload Size

```nginx
# In nginx.conf location block
client_max_body_size 20M;
```

### Optimize Python

```bash
# Install uvicorn with optimizations
pip install uvicorn[standard]

# Use multiple workers (in systemd service)
ExecStart=/var/www/aman-ga/backend/venv/bin/uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4
```

---

## 📞 Quick Help

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check if backend is running |
| 404 Not Found | Check Nginx config |
| 500 Internal Error | Check backend logs |
| Upload fails | Check file size limit |
| OCR fails | Check Tesseract installation |
| Slow performance | Check system resources |

---

## 🎉 Default Credentials

```
Email: admin@amanga.id
Password: admin123

Finance:
Email: finance@amanga.id
Password: admin123
```

**⚠️ Change these immediately in production!**

---

## 📚 Documentation

- `DEPLOYMENT-SERVER.md` - Full deployment guide
- `SELF-LEARNING-OCR.md` - OCR system docs
- `SECURITY-IMPROVEMENTS.md` - Security features
- `DOCUMENTATION-INDEX.md` - Complete index

---

**Version**: 2.1.0 | **Last Updated**: March 19, 2026
