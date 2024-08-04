#!/bin/bash

set -e

# Define variables
APP_DIR="/var/www/midfield-backend"
VENV_DIR="$APP_DIR/venv"
GUNICORN_SOCKET="$APP_DIR/myapp.sock"
GUNICORN_LOG="$APP_DIR/gunicorn.log"
GUNICORN_ACCESS_LOG="$APP_DIR/gunicorn-access.log"
NGINX_CONF="/etc/nginx/sites-available/midfield-backend"

# Create app folder if it doesn't exist
echo "Creating app folder"
sudo mkdir -p $APP_DIR

# Sync files to app folder
echo "Syncing files to app folder"
rsync -av --exclude 'venv' . $APP_DIR

# Navigate to the app directory
cd $APP_DIR

# Move .env file if it exists
if [ -f env ]; then
    echo "Moving .env file"
    sudo mv env .env
else
    echo ".env file not found, skipping"
fi

# Changing ownership to the current user
echo "Changing ownership to the current user"
sudo chown -R $USER:$USER $APP_DIR

# Install Python, pip, and venv if not already installed
sudo apt-get update
echo "Installing python, pip, and venv"
sudo apt-get install -y python3 python3-pip python3-venv

# Install system dependencies for building some Python packages
echo "Installing system dependencies"
sudo apt-get install -y pkg-config cmake

# Create and activate a virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment"
    python3 -m venv $VENV_DIR
fi

echo "Activating virtual environment"
source $VENV_DIR/bin/activate

# Install application dependencies from requirements.txt
echo "Installing application dependencies from requirements.txt"
pip install -r requirements.txt

# Install Gunicorn
echo "Installing Gunicorn"
pip install gunicorn

# Update and install Nginx if not already installed
if ! command -v nginx > /dev/null; then
    echo "Installing Nginx"
    sudo apt-get update
    sudo apt-get install -y nginx
fi

# Configure Nginx to act as a reverse proxy if not already configured
if [ ! -f $NGINX_CONF ]; then
    echo "Configuring Nginx"
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo bash -c "cat > $NGINX_CONF <<EOF
server {
    listen 80;
    server_name api.midfield.ai;

    location / {
        include proxy_params;
        proxy_pass http://unix:$GUNICORN_SOCKET;
    }

    error_log /var/log/nginx/error.log;
    access_log /var/log/nginx/access.log;
}
EOF"

    sudo ln -s $NGINX_CONF /etc/nginx/sites-enabled/
    sudo systemctl restart nginx
else
    echo "Nginx reverse proxy configuration already exists."
fi

# Stop any existing Gunicorn process
echo "Stopping any existing Gunicorn process"
sudo pkill gunicorn || true

# Activate the virtual environment and start Gunicorn with the Django application
echo "Starting Gunicorn"
source $VENV_DIR/bin/activate
$VENV_DIR/bin/gunicorn --workers 3 --bind unix:$GUNICORN_SOCKET midfield_backend.wsgi:application --daemon --user www-data --group www-data --log-file $GUNICORN_LOG --access-logfile $GUNICORN_ACCESS_LOG

# Set permissions
echo "Setting permissions"
sudo chown -R www-data:www-data $APP_DIR

echo "Deployment complete 🚀"
