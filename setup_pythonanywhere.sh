#!/bin/bash
# ==============================================================================
# HireU - Automated PythonAnywhere Deployment Script
# ==============================================================================
# Usage in PythonAnywhere Bash Console:
#   cd ~
#   git clone https://github.com/unnikrishnan803/hire_u.git
#   cd hire_u
#   chmod +x setup_pythonanywhere.sh
#   ./setup_pythonanywhere.sh
# ==============================================================================

set -e

echo "🚀 [1/5] Starting HireU deployment on PythonAnywhere..."

# Detect home directory and current user
PA_USER=$(whoami)
PROJECT_DIR="$HOME/hire_u"
VENV_DIR="$HOME/.virtualenvs/hireu-env"

# Ensure we are in the project folder
cd "$PROJECT_DIR" || cd "$(pwd)"

echo "📦 [2/5] Setting up Python 3.10 virtual environment at $VENV_DIR..."
if [ ! -d "$VENV_DIR" ]; then
    python3.10 -m venv "$VENV_DIR" || python3 -m venv "$VENV_DIR"
fi

# Activate virtualenv
source "$VENV_DIR/bin/activate"

echo "📥 [3/5] Installing project dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗄️ [4/5] Running migrations..."
python manage.py migrate

echo "🎨 [5/5] Collecting static assets..."
python manage.py collectstatic --noinput

echo ""
echo "=============================================================================="
echo "✅ DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "=============================================================================="
echo ""
echo "👉 NEXT STEPS IN PYTHONANYWHERE WEB TAB (https://www.pythonanywhere.com/user/$PA_USER/web/):"
echo ""
echo "1. Source code:"
echo "   /home/$PA_USER/hire_u"
echo ""
echo "2. Working directory:"
echo "   /home/$PA_USER/hire_u"
echo ""
echo "3. Virtualenv:"
echo "   /home/$PA_USER/.virtualenvs/hireu-env"
echo ""
echo "4. Static files table:"
echo "   URL:    /static/"
echo "   Directory: /home/$PA_USER/hire_u/staticfiles"
echo ""
echo "   URL:    /media/"
echo "   Directory: /home/$PA_USER/hire_u/media"
echo ""
echo "5. In the WSGI configuration file link (click the link in Web tab):"
echo "   Replace the contents with:"
echo "   -------------------------------------------------------------"
echo "   import os"
echo "   import sys"
echo "   path = '/home/$PA_USER/hire_u'"
echo "   if path not in sys.path:"
echo "       sys.path.append(path)"
echo "   os.environ['DJANGO_SETTINGS_MODULE'] = 'hireu.settings'"
echo "   from django.core.wsgi import get_wsgi_application"
echo "   application = get_wsgi_application()"
echo "   -------------------------------------------------------------"
echo ""
echo "6. Click the green 'Reload <username>.pythonanywhere.com' button at the top!"
echo "=============================================================================="
