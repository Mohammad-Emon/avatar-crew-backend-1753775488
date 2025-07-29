#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting deployment of Avatar-Crew backend to Fly.io..."

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ Error: flyctl is not installed. Please install it from https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

# Check if user is logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "🔐 Please log in to Fly.io..."
    flyctl auth login
fi

# Set the app name (you can change this)
APP_NAME="avatar-crew-backend"

# Check if the app already exists
if flyctl status --app $APP_NAME &> /dev/null; then
    echo "🔄 Updating existing app: $APP_NAME"
    
    # Deploy the app
    flyctl deploy --app $APP_NAME
else
    echo "✨ Creating new app: $APP_NAME"
    
    # Launch the app
    flyctl launch --name $APP_NAME --region sin --no-deploy
    
    # Set environment variables
    echo "🔑 Setting environment variables..."
    if [ -f .env ]; then
        # Read .env file and set secrets
        grep -v '^#' .env | grep -v '^$' | while read -r line; do
            key=$(echo $line | cut -d '=' -f1)
            value=$(echo $line | cut -d '=' -f2-)
            echo "Setting $key"
            flyctl secrets set "$key=$value" --app $APP_NAME
        done
    else
        echo "⚠️  No .env file found. Please set your environment variables manually using:"
        echo "   flyctl secrets set KEY=VALUE --app $APP_NAME"
    fi
    
    # Deploy the app
    flyctl deploy --app $APP_NAME
fi

echo "✅ Deployment complete!"
echo "🔗 Your app is available at: https://$APP_NAME.fly.dev"
