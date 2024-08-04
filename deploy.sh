#!/bin/bash

set -e

# Creating app folder
echo "Creating app folder"
sudo mkdir -p /var/www/midfield-backend

# Moving files to app folder
echo "Moving files to app folder"
sudo mv * /var/www/midfield-backend

# Navigate to the app directory
cd /var/www/midfield-backend/
sudo mv env .env

# Changing ownership to the current user
echo "Changing ownership to the current user"
sudo chown -R $USER:$USER /var/www/midfield-backend/

# Installing Python, pip, and venv
sudo apt-get update
echo "Installing python, pip, and venv"
sudo apt-get install -y python3 python3-pip python3-venv

# Create and activate a virtual environment
echo "Creating and activating virtual environment"
python3 -m venv venv
source venv/bin/activate

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
if [ ! -f /etc/nginx/sites-available/midfield-backend ]; then
    echo "Configuring Nginx"
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo bash -c 'cat > /etc/nginx/sites-available/midfield-backend <<EOF
server {
    listen 80;
    server_name _;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/midfield-backend/myapp.sock;
    }

    error_log /var/log/nginx/error.log;
    access_log /var/log/nginx/access.log;
}
EOF'

    sudo ln -s /etc/nginx/sites-available/midfield-backend /etc/nginx/sites-enabled/
    sudo systemctl restart nginx
else
    echo "Nginx reverse proxy configuration already exists."
fi

# Stop any existing Gunicorn process
echo "Stopping any existing Gunicorn process"
sudo pkill gunicorn || true

# Activate the virtual environment and start Gunicorn with the Django application
echo "Starting Gunicorn"
source venv/bin/activate
venv/bin/gunicorn --workers 3 --bind unix:/var/www/midfield-backend/myapp.sock midfield_backend.wsgi:application --daemon --user www-data --group www-data --log-file /var/www/midfield-backend/gunicorn.log --access-logfile /var/www/midfield-backend/gunicorn-access.log

# Set permissions
echo "Setting permissions"
sudo chown -R www-data:www-data /var/www/midfield-backend

echo "Deployment complete 🚀"
