# Aman ga? - Alibaba Cloud Deployment Guide

## Overview
This guide explains how to deploy the Aman ga? application on Alibaba Cloud's simple application server. The application runs in **demo mode** without requiring a database service.

## Features in Demo Mode
- ✅ Full receipt validation functionality
- ✅ OCR extraction with confidence scoring
- ✅ Image manipulation detection
- ✅ Deepfake detection
- ✅ Multi-layer validation system
- ✅ Self-learning OCR system
- ✅ User authentication and authorization
- ✅ Admin dashboard
- ✅ All functionality preserved
- ❌ No persistent data storage (data resets on restart)

## Prerequisites
- Alibaba Cloud ECS instance (any Linux distribution)
- Root access to the server
- At least 2GB RAM and 20GB disk space

## Deployment Steps

### 1. Connect to Your Server
```bash
ssh root@YOUR_SERVER_IP
```

### 2. Download the Deployment Script
```bash
wget https://raw.githubusercontent.com/Therealratoshen/aman-ga/main/alibaba-deploy.sh
chmod +x alibaba-deploy.sh
```

### 3. Run the Deployment Script
```bash
sudo ./alibaba-deploy.sh
```

### 4. Access Your Application
Once deployment is complete, you can access:
- **Frontend**: `http://YOUR_SERVER_IP`
- **API Documentation**: `http://YOUR_SERVER_IP/docs`
- **Health Check**: `http://YOUR_SERVER_IP/health`

## Demo Credentials
- **Admin**: `admin@amanga.id` / `admin123`
- **Finance**: `finance@amanga.id` / `admin123`

## Management Commands
- **Start**: `sudo systemctl start aman-ga`
- **Stop**: `sudo systemctl stop aman-ga`
- **Restart**: `sudo systemctl restart aman-ga`
- **Status**: `sudo systemctl status aman-ga`
- **Logs**: `sudo journalctl -u aman-ga -f`

## Important Notes
1. **Demo Mode**: The application runs with an in-memory database that resets on restart
2. **No External Dependencies**: No database service required for demo operation
3. **Persistent Storage**: For production, configure Supabase by editing `/var/www/aman-ga/backend/.env`
4. **Security**: The deployment includes firewall configuration and security headers

## Architecture
- **Frontend**: Static files served by Nginx
- **Backend**: FastAPI application with OCR and validation services
- **Proxy**: Nginx reverse proxy handles routing
- **Service Manager**: Systemd manages the backend service

## Customization
To customize the application for your needs:
1. Edit the `.env` file at `/var/www/aman-ga/backend/.env`
2. Modify the nginx configuration at `/etc/nginx/sites-available/aman-ga`
3. Adjust the systemd service at `/etc/systemd/system/aman-ga.service`

## Troubleshooting
- Check service status: `sudo systemctl status aman-ga`
- View logs: `sudo journalctl -u aman-ga -f`
- Check nginx: `sudo nginx -t`
- Verify ports are open in your Alibaba Cloud security groups

## Production Deployment
For production use:
1. Set up Supabase account
2. Update the `.env` file with Supabase credentials
3. Set `MOCK_MODE=False`
4. Restart the service: `sudo systemctl restart aman-ga`

## Support
For issues or questions, please refer to the main project documentation or create an issue in the repository.