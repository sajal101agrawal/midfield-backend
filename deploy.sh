#!/bin/bash

set -e

# Define variables
APP_DIR="/var/www/midfield-backend"
VENV_DIR="$APP_DIR/venv"
GUNICORN_SOCKET="$APP_DIR/myapp.sock"
GUNICORN_LOG="$APP_DIR/gunicorn.log"
GUNICORN_ACCESS_LOG="$APP_DIR/gunicorn-access.log"
NGINX_CONF="/etc/nginx/sites-available/midfield-backend"
GUARDRAILS_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDExNTM0Mzg0MzQxNTkzMTI3NDE5NCIsImFwaUtleUlkIjoiMzg4ZjljNmItODhlNC00NGNiLWE2MTgtN2EyZGNmYzg5NTAxIiwiaWF0IjoxNzIyNzg5NzI1LCJleHAiOjQ4NzYzODk3MjV9.qwHppDtqhOTRurS23e_1JYMNtD-v-Cdlx3Iv85-lEKQ"

# Create app folder if it doesn't exist
echo "Creating app folder"
sudo mkdir -p $APP_DIR

# Sync files to app folder
echo "Syncing files to app folder"
sudo rsync -av --exclude 'venv' . $APP_DIR

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

# Install expect
echo "Installing expect"
sudo apt-get install -y expect

# Create and activate a virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment"
    sudo python3 -m venv $VENV_DIR
    sudo chown -R $USER:$USER $VENV_DIR
fi

echo "Activating virtual environment"
source $VENV_DIR/bin/activate

# Install application dependencies from requirements.txt
echo "Installing application dependencies from requirements.txt"
pip install -r requirements.txt

# Configure Guardrails API key using expect
echo "Configuring Guardrails API key"
expect << EOF
spawn guardrails configure
expect "Enable anonymous metrics reporting? \[Y/n\]:"
send "n\r"
expect "Do you wish to use remote inferencing? \[Y/n\]:"
send "n\r"
expect "API Key:"
send "$GUARDRAILS_API_KEY\r"
expect eof
EOF

# Function to install Guardrails hub package if not already installed
install_guardrails_hub_package() {
    PACKAGE=$1
    if ! guardrails hub list | grep -q "$PACKAGE"; then
        echo "Installing $PACKAGE"
        guardrails hub install $PACKAGE
    else
        echo "$PACKAGE is already installed"
    fi
}

# Install Guardrails hub packages
echo "Installing Guardrails hub packages"
install_guardrails_hub_package hub://arize-ai/dataset_embeddings_guardrails
install_guardrails_hub_package hub://scb-10x/correct_language
install_guardrails_hub_package hub://guardrails/detect_prompt_injection
install_guardrails_hub_package hub://aryn/extractive_summary
install_guardrails_hub_package hub://guardrails/nsfw_text
install_guardrails_hub_package hub://guardrails/provenance_embeddings
install_guardrails_hub_package hub://guardrails/qa_relevance_llm_eval
install_guardrails_hub_package hub://tryolabs/restricttotopic
install_guardrails_hub_package hub://guardrails/secrets_present
install_guardrails_hub_package hub://guardrails/similar_to_previous_values
install_guardrails_hub_package hub://guardrails/wiki_provenance
install_guardrails_hub_package hub://hyparam/csv_validator
install_guardrails_hub_package hub://guardrails/ends_with
install_guardrails_hub_package hub://cartesia/financial_tone
install_guardrails_hub_package hub://guardrails/llm_critic
install_guardrails_hub_package hub://cartesia/mentions_drugs
install_guardrails_hub_package hub://guardrails/politeness_check
install_guardrails_hub_package hub://guardrails/reading_level
install_guardrails_hub_package hub://guardrails/redundant_sentences
install_guardrails_hub_package hub://guardrails/response_evaluator
install_guardrails_hub_package hub://guardrails/sensitive_topics
install_guardrails_hub_package hub://guardrails/two_words
install_guardrails_hub_package hub://guardrails/uppercase
install_guardrails_hub_package hub://guardrails/valid_choices
install_guardrails_hub_package hub://guardrails/valid_length
install_guardrails_hub_package hub://reflex/valid_python
install_guardrails_hub_package hub://guardrails/valid_sql
install_guardrails_hub_package hub://guardrails/web_sanitization
install_guardrails_hub_package hub://guardrails/valid_url
install_guardrails_hub_package hub://guardrails/valid_range
install_guardrails_hub_package hub://guardrails/valid_open_api_spec
install_guardrails_hub_package hub://guardrails/valid_json
install_guardrails_hub_package hub://guardrails/valid_address
install_guardrails_hub_package hub://guardrails/unusual_prompt
install_guardrails_hub_package hub://numbersstation/sql_column_presence
install_guardrails_hub_package hub://guardrails/responsiveness_check
install_guardrails_hub_package hub://guardrails/regex_match
install_guardrails_hub_package hub://guardrails/reading_time
install_guardrails_hub_package hub://cartesia/quotes_price
install_guardrails_hub_package hub://guardrails/one_line
install_guardrails_hub_package hub://guardrails/lowercase
install_guardrails_hub_package hub://guardrails/has_url
install_guardrails_hub_package hub://guardrails/exclude_sql_predicates
install_guardrails_hub_package hub://guardrails/endpoint_is_reachable
install_guardrails_hub_package hub://guardrails/toxic_language
install_guardrails_hub_package hub://guardrails/similar_to_document
install_guardrails_hub_package hub://guardrails/saliency_check
install_guardrails_hub_package hub://arize-ai/relevancy_evaluator
install_guardrails_hub_package hub://guardrails/provenance_llm
install_guardrails_hub_package hub://guardrails/profanity_free
install_guardrails_hub_package hub://guardrails/logic_check
install_guardrails_hub_package hub://guardrails/gibberish_text
install_guardrails_hub_package hub://guardrails/extracted_summary_sentences_match
install_guardrails_hub_package hub://guardrails/detect_pii
install_guardrails_hub_package hub://guardrails/competitor_check

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

# Export PYTHONPATH to ensure the project module is found
export PYTHONPATH=$PYTHONPATH:$APP_DIR

sudo $VENV_DIR/bin/gunicorn --workers 3 --bind unix:$GUNICORN_SOCKET midfield.wsgi:application --daemon --user www-data --group www-data --log-file $GUNICORN_LOG --access-logfile $GUNICORN_ACCESS_LOG

# Set permissions
echo "Setting permissions"
sudo chown -R www-data:www-data $APP_DIR

# Display status for debugging
echo "Checking Gunicorn status"
ps aux | grep gunicorn

echo "Checking Gunicorn log"
sudo cat $GUNICORN_LOG

echo "Checking Nginx error log"
sudo cat /var/log/nginx/error.log

echo "Deployment complete 🚀"
