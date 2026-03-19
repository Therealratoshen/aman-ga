#!/bin/bash
#===============================================================================
# Aman ga? v2.1 - Automated Deployment Script
# For Simple Application Server (Alibaba Cloud ECS, DigitalOcean, etc.)
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
echo -e "${BLUE}║   Aman ga? v2.1 - Deployment Script                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (sudo ./deploy.sh)${NC}"
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
echo -e "${BLUE}📦 Step 1/8: Installing system dependencies...${NC}"

if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt update
    apt upgrade -y
    apt install -y python3 python3-pip python3-venv python3-dev
    apt install -y tesseract-ocr tesseract-ocr-ind libmagic1
    apt install -y nginx git curl wget build-essential
    apt install -y supervisor  # Alternative to systemd
    
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    yum update -y
    yum install -y python3 python3-pip
    yum install -y tesseract tesseract-langpack-eng libmagic
    yum install -y nginx git curl wget gcc gcc-c++
    yum install -y epel-release
    
else
    echo -e "${RED}❌ Unsupported OS: $OS${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} System dependencies installed"

#===============================================================================
# Step 2: Clone/Setup Application
#===============================================================================
echo ""
echo -e "${BLUE}📂 Step 2/8: Setting up application...${NC}"

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
    git clone https://github.com/Therealratoshen/aman-ga.git
fi

echo -e "${GREEN}✓${NC} Application setup complete"

#===============================================================================
# Step 3: Setup Python Environment
#===============================================================================
echo ""
echo -e "${BLUE}🐍 Step 3/8: Setting up Python environment...${NC}"

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
# Step 4: Configure Environment
#===============================================================================
echo ""
echo -e "${BLUE}⚙️  Step 4/8: Configuring environment...${NC}"

# Create .env if not exists
if [ ! -f "$APP_DIR/backend/.env" ]; then
    echo "Creating .env file..."
    cat > $APP_DIR/backend/.env << EOF
# Supabase Configuration
# Get these from https://supabase.com
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# JWT Settings
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Mock Mode (True for testing without Supabase)
MOCK_MODE=True

# Application Settings
APP_NAME=Aman ga?
DEBUG=False
EOF
    echo -e "${YELLOW}⚠️  Please edit $APP_DIR/backend/.env with your settings${NC}"
else
    echo -e "${GREEN}✓${NC} .env already exists"
fi

echo -e "${GREEN}✓${NC} Environment configured"

#===============================================================================
# Step 5: Setup Nginx
#===============================================================================
echo ""
echo -e "${BLUE}🌐 Step 5/8: Configuring Nginx...${NC}"

# Copy Nginx config
if [ -f "$APP_DIR/nginx.conf" ]; then
    cp $APP_DIR/nginx.conf /etc/nginx/sites-available/$APP_NAME
    ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
else
    echo -e "${RED}❌ nginx.conf not found${NC}"
    exit 1
fi

# Test Nginx configuration
nginx -t

echo -e "${GREEN}✓${NC} Nginx configured"

#===============================================================================
# Step 6: Setup Systemd Service
#===============================================================================
echo ""
echo -e "${BLUE}🔧 Step 6/8: Setting up systemd service...${NC}"

if [ -f "$APP_DIR/aman-ga.service" ]; then
    cp $APP_DIR/aman-ga.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable $APP_NAME
else
    echo -e "${RED}❌ aman-ga.service not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Systemd service configured"

#===============================================================================
# Step 7: Setup Firewall
#===============================================================================
echo ""
echo -e "${BLUE}🔒 Step 7/8: Configuring firewall...${NC}"

# Check if UFW is available
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
    echo "Firewall configured with UFW"
else
    # Check if firewalld is available
    if command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --reload
        echo "Firewall configured with firewalld"
    else
        echo -e "${YELLOW}⚠️  No firewall tool found. Configure manually.${NC}"
    fi
fi

echo -e "${GREEN}✓${NC} Firewall rules applied"

#===============================================================================
# Step 8: Start Services
#===============================================================================
echo ""
echo -e "${BLUE}🚀 Step 8/8: Starting services...${NC}"

# Start backend
systemctl start $APP_NAME
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
echo -e "${GREEN}║          ✅ Deployment Complete!                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo -e "${BLUE}📊 Application Details:${NC}"
echo "  Frontend:  http://$SERVER_IP"
echo "  Backend:   http://$SERVER_IP:8000"
echo "  API Docs:  http://$SERVER_IP/docs"
echo "  Health:    http://$SERVER_IP/health"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "  1. Edit .env file with your Supabase credentials"
echo "  2. Restart service: sudo systemctl restart $APP_NAME"
echo "  3. Set up SSL (optional): sudo certbot --nginx"
echo "  4. Check logs: sudo journalctl -u $APP_NAME -f"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "  - Currently running in MOCK MODE (no database)"
echo "  - Set MOCK_MODE=False in .env for production"
echo "  - Configure Supabase for persistent storage"
echo ""
echo -e "${GREEN}Happy coding! 🎉${NC}"
