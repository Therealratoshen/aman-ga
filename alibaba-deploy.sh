#!/bin/bash
#===============================================================================
# Aman ga? v2.1 - Alibaba Cloud Simple Application Server Deployment
# For demo/POC operation without database service
#===============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="aman-ga"
APP_DIR="/var/www/aman-ga"
PYTHON_VERSION="3.10"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Aman ga? v2.1 - Alibaba Cloud Deployment          ║${NC}"
echo -e "${BLUE}║   (Demo Mode - No Database Service)                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root (sudo ./alibaba-deploy.sh)${NC}"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo -e "${RED}❌ Cannot detect OS${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Detected OS: ${YELLOW}$OS${NC}"

#===============================================================================
# Step 1: Install System Dependencies
#===============================================================================
echo ""
echo -e "${BLUE}📦 Step 1/7: Installing system dependencies...${NC}"

if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt update
    apt upgrade -y
    apt install -y python3 python3-pip python3-venv python3-dev
    apt install -y tesseract-ocr tesseract-ocr-ind libmagic1
    apt install -y nginx git curl wget build-essential
    apt install -y supervisor

elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "rocky" ] || [ "$OS" = "almalinux" ]; then
    yum update -y
    yum install -y python3 python3-pip
    yum install -y tesseract tesseract-langpack-eng libmagic
    yum install -y nginx git curl wget gcc gcc-c++
    yum install -y epel-release
    yum install -y supervisor

else
    echo -e "${RED}❌ Unsupported OS: $OS${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} System dependencies installed"

#===============================================================================
# Step 2: Clone/Setup Application
#===============================================================================
echo ""
echo -e "${BLUE}📂 Step 2/7: Setting up application...${NC}"

# Create directory
mkdir -p $APP_DIR

# Check if already exists
if [ -d "$APP_DIR/.git" ]; then
    echo -e "${YELLOW}⚠ Application already exists. Pulling latest changes...${NC}"
    cd $APP_DIR
    git pull
else
    # Clone repository
    echo "Cloning repository..."
    cd /var/www
    git clone https://github.com/Therealratoshen/aman-ga.git aman-ga
fi

echo -e "${GREEN}✓${NC} Application setup complete"

#===============================================================================
# Step 3: Setup Python Environment
#===============================================================================
echo ""
echo -e "${BLUE}🐍 Step 3/7: Setting up Python environment...${NC}"

cd $APP_DIR/backend

# Create virtual environment
python3 -m venv venv

# Activate and upgrade
source venv/bin/activate
pip install --upgrade pip

# Install requirements
echo "Installing Python packages..."
pip install -r requirements.txt

echo -e "${GREEN}✓${NC} Python environment ready"

#===============================================================================
# Step 4: Configure Environment for Demo Mode
#===============================================================================
echo ""
echo -e "${BLUE}⚙️  Step 4/7: Configuring environment (Demo Mode)...${NC}"

# Create .env file for demo mode
cat > $APP_DIR/backend/.env << EOF
# Supabase Configuration (Not needed for demo mode)
# These values will trigger mock mode
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# JWT Settings
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
APP_NAME=Aman ga?
DEBUG=False

# DEMO MODE - No database service needed
MOCK_MODE=True
EOF

echo -e "${GREEN}✓${NC} Environment configured for demo mode"

#===============================================================================
# Step 5: Setup Nginx
#===============================================================================
echo ""
echo -e "${BLUE}🌐 Step 5/7: Configuring Nginx...${NC}"

# Create nginx config for the application
cat > /etc/nginx/sites-available/$APP_NAME << 'EOF'
server {
    listen 80;
    server_name _;

    # Frontend (static files)
    location / {
        root /var/www/aman-ga/frontend/public;
        index index.html;
        try_files $uri $uri/ /index.html;

        # Security headers
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }

    # Backend API routes
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
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /receipt {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase max upload size for receipt validation
        client_max_body_size 10M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 60s;
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

    location /payment {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /me {
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
        access_log off;
    }

    location /validation {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /receipt-formats {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API documentation
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Nginx error pages
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

echo -e "${GREEN}✓${NC} Nginx configured"

#===============================================================================
# Step 6: Setup Systemd Service
#===============================================================================
echo ""
echo -e "${BLUE}🔧 Step 6/7: Setting up systemd service...${NC}"

# Create systemd service file
cat > /etc/systemd/system/$APP_NAME.service << 'EOF'
[Unit]
Description=Aman ga? Backend API - Payment Verification System (Demo Mode)
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/aman-ga/backend
Environment="PATH=/var/www/aman-ga/backend/venv/bin"
Environment="MOCK_MODE=True"
ExecStart=/var/www/aman-ga/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=aman-ga

# Security hardening
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload
systemctl enable $APP_NAME

echo -e "${GREEN}✓${NC} Systemd service configured"

#===============================================================================
# Step 7: Setup Firewall
#===============================================================================
echo ""
echo -e "${BLUE}🔒 Step 7/7: Configuring firewall...${NC}"

# Check if UFW is available
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
    ufw --force enable
    echo -e "${GREEN}✓${NC} Firewall configured with UFW"
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --permanent --add-service=ssh
    firewall-cmd --reload
    echo -e "${GREEN}✓${NC} Firewall configured with firewalld"
else
    echo -e "${YELLOW}⚠️  No firewall tool found. Configure manually if needed.${NC}"
fi

#===============================================================================
# Start Services
#===============================================================================
echo ""
echo -e "${BLUE}🚀 Starting services...${NC}"

# Start backend
systemctl start $APP_NAME
sleep 5  # Wait for service to start
systemctl status $APP_NAME --no-pager

# Start Nginx
systemctl restart nginx
systemctl status nginx --no-pager

echo -e "${GREEN}✓${NC} Services started"

#===============================================================================
# Deployment Complete
#===============================================================================
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✅ Alibaba Cloud Deployment Complete!        ║${NC}"
echo -e "${GREEN}║              Demo Mode - No Database Service          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)

echo -e "${BLUE}📊 Application Details:${NC}"
echo "  Frontend:  http://$SERVER_IP"
echo "  Backend:   http://$SERVER_IP:8000"
echo "  API Docs:  http://$SERVER_IP/docs"
echo "  Health:    http://$SERVER_IP/health"
echo ""
echo -e "${BLUE}📝 Demo Credentials:${NC}"
echo "  Admin: admin@amanga.id / admin123"
echo "  Finance: finance@amanga.id / admin123"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo "  Start:     sudo systemctl start $APP_NAME"
echo "  Stop:      sudo systemctl stop $APP_NAME"
echo "  Restart:   sudo systemctl restart $APP_NAME"
echo "  Status:    sudo systemctl status $APP_NAME"
echo "  Logs:      sudo journalctl -u $APP_NAME -f"
echo ""
echo -e "${YELLOW}ℹ️  Information:${NC}"
echo "  - Running in DEMO MODE (no database service needed)"
echo "  - All data is in-memory and resets on restart"
echo "  - Perfect for demonstration and testing"
echo "  - For production, configure Supabase in .env"
echo ""
echo -e "${GREEN}🎉 Aman ga? is now running on your Alibaba Cloud server!${NC}"