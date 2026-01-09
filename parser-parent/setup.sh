#!/bin/bash
# Upside Hackathon Setup Script
set -e

echo "Upside Hackathon Setup"
echo "----------------------"

# Check if .env exists
if [ -f ".env" ]; then
    echo ".env file found"

    if grep -q "your-openai-api-key-here" .env; then
        echo "WARNING: .env file still has a placeholder API key."
        echo "Edit .env and replace 'your-openai-api-key-here' with your actual key."
        echo "Get your key from: https://platform.openai.com/api-keys"
        read -p "Press Enter after updating the .env file..."
    else
        echo "OpenAI API key appears to be set"
    fi
else
    echo ".env file not found. Creating from template..."

    cat > .env << 'EOF'
# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=your-openai-api-key-here

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=upside_db

# Flask Configuration
FLASK_ENV=development
DEBUG=True
EOF

    echo ".env file created"
    echo "Edit .env and replace 'your-openai-api-key-here' with your actual key."
    echo "Get your key from: https://platform.openai.com/api-keys"
    read -p "Press Enter after updating the .env file..."
fi

echo "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
fi
echo "Docker is running"

echo "Checking docker-compose..."
if ! command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi
echo "Using: $DOCKER_COMPOSE"

echo "Building Docker images..."
$DOCKER_COMPOSE build

echo "Starting services..."
$DOCKER_COMPOSE up -d

echo "Waiting for services..."
sleep 10

echo "Checking service health..."
if curl -s http://localhost:7312/health > /dev/null; then
    echo "API is running at http://localhost:7312"
else
    echo "API may not be ready. Check logs:"
    echo "  $DOCKER_COMPOSE logs api"
fi

if $DOCKER_COMPOSE exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "PostgreSQL is running"
else
    echo "PostgreSQL may not be ready yet"
fi

echo "Setup complete"

echo "Next steps:"
echo "  Test API:     curl http://localhost:7312/health"
echo "  View logs:   $DOCKER_COMPOSE logs -f api"
echo "  Stop stack:  $DOCKER_COMPOSE down"

echo "Documentation:"
echo "  parser/API_DOCUMENTATION.md"
echo "  parser/QUICKSTART.md"
echo "  SECURITY_SETUP.md"
