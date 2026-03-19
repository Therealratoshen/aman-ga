#!/bin/bash
# Installation Script for Aman ga? v2.0 Security Updates
# Run this script to install all dependencies and set up the system

set -e  # Exit on error

echo "============================================================"
echo "🔒 Aman ga? v2.0 - Security Installation Script"
echo "============================================================"
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "🍎 Detected macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "🐧 Detected Linux"
else
    echo "⚠️  Unsupported OS: $OSTYPE"
    exit 1
fi

# Install system dependencies
echo ""
echo "📦 Installing system dependencies..."

if [[ "$OS" == "macos" ]]; then
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Please install it first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    echo "🍺 Installing Tesseract OCR..."
    brew install tesseract
    
    echo "🍺 Installing libmagic..."
    brew install libmagic
    
    echo "✅ System dependencies installed"
    
elif [[ "$OS" == "linux" ]]; then
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        echo "📦 Using apt-get..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr libmagic1
        
        # Try to install Indonesian language pack
        echo "🌐 Installing Indonesian language pack for OCR..."
        sudo apt-get install -y tesseract-ocr-ind || echo "⚠️  Indonesian pack not available"
        
    elif command -v yum &> /dev/null; then
        echo "📦 Using yum..."
        sudo yum install -y tesseract tesseract-langpack-eng libmagic
        
    elif command -v dnf &> /dev/null; then
        echo "📦 Using dnf..."
        sudo dnf install -y tesseract tesseract-langpack-eng libmagic
        
    else
        echo "❌ Unsupported package manager. Please install manually:"
        echo "   - Tesseract OCR: https://github.com/tesseract-ocr/tesseract"
        echo "   - libmagic: https://github.com/file/file"
        exit 1
    fi
    
    echo "✅ System dependencies installed"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."

cd "$(dirname "$0")/backend"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "🐍 Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

echo "✅ Python dependencies installed"

# Run tests
echo ""
echo "🧪 Running validation tests..."
python test_validation.py

# Create .env if it doesn't exist
echo ""
echo "⚙️  Setting up environment..."

if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "⚠️  Please edit .env and add your Supabase credentials"
    else
        cat > .env << EOF
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# JWT Settings
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Mock Mode (set to False for production)
MOCK_MODE=True
EOF
        echo "✅ Created .env file with default values"
        echo "⚠️  Please edit .env and add your credentials"
    fi
else
    echo "✅ .env already exists"
fi

# Database setup
echo ""
echo "🗄️  Database Setup"
echo "If using Supabase:"
echo "1. Go to https://supabase.com"
echo "2. Create a new project or select existing"
echo "3. Go to SQL Editor"
echo "4. Run the contents of: ../database/schema.sql"
echo ""
echo "If using Mock Mode (for testing):"
echo "- No database setup needed!"
echo "- Data will be stored in memory"

# Final instructions
echo ""
echo "============================================================"
echo "✅ Installation Complete!"
echo "============================================================"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload --port 8000"
echo ""
echo "2. Open browser to: http://localhost:8000/docs"
echo ""
echo "3. Test the API or use the frontend:"
echo "   Frontend URL: http://localhost:8000/app.html"
echo ""
echo "4. Demo credentials:"
echo "   Email: admin@amanga.id"
echo "   Password: admin123"
echo ""
echo "============================================================"
echo "📖 Documentation:"
echo "   - SECURITY-IMPROVEMENTS.md"
echo "   - IMPLEMENTATION-SUMMARY.md"
echo "   - ../README.md"
echo "============================================================"
echo ""
