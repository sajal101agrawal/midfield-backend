#!/bin/bash

# Creating app folder
echo "Creating app folder"
sudo mkdir -p /var/www/midfield-backend

# Moving files to app folder
echo "Moving files to app folder"
sudo mv * /var/www/midfield-backend

# Navigate to the app directory
cd /var/www/midfield-backend/
sudo mv env .env

# Installing Python and pip
sudo apt-get update
echo "Installing python and pip"
sudo apt-get install -y python3 python3-pip

# Install application dependencies from requirements.txt
echo "Installing application dependencies from requirements.txt"
sudo pip3 install -r requirements.txt

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
}
EOF'

    sudo ln -s /etc/nginx/sites-available/midfield-backend /etc/nginx/sites-enabled/
    sudo systemctl restart nginx
else
    echo "Nginx reverse proxy configuration already exists."
fi

# Stop any existing Gunicorn process
echo "Stopping any existing Gunicorn process"
sudo pkill gunicorn

# Start Gunicorn with the Django application
echo "Starting Gunicorn"
sudo gunicorn --workers 3 --bind unix:/var/www/midfield-backend/myapp.sock midfield_backend.wsgi:application --daemon --user www-data --group www-data

echo "Deployment complete 🚀"
