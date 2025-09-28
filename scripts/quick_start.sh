#!/bin/bash
set -e

echo "🚀 Voice Agent Quick Start"
echo "=========================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check .env file
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Creating from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please fill in your API keys in .env file${NC}"
    exit 1
fi

# Check if required API keys are set
source .env
missing_keys=()

[ -z "$LIVEKIT_URL" ] && missing_keys+=("LIVEKIT_URL")
[ -z "$LIVEKIT_API_KEY" ] && missing_keys+=("LIVEKIT_API_KEY")
[ -z "$LIVEKIT_API_SECRET" ] && missing_keys+=("LIVEKIT_API_SECRET")
[ -z "$OPENAI_API_KEY" ] && missing_keys+=("OPENAI_API_KEY")
[ -z "$DEEPGRAM_API_KEY" ] && missing_keys+=("DEEPGRAM_API_KEY")
[ -z "$ELEVENLABS_API_KEY" ] && missing_keys+=("ELEVENLABS_API_KEY")

if [ ${#missing_keys[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing API keys in .env:${NC}"
    printf '%s\n' "${missing_keys[@]}"
    echo ""
    echo "Get your API keys from:"
    echo "  • LiveKit: https://cloud.livekit.io"
    echo "  • OpenAI: https://platform.openai.com/api-keys"
    echo "  • Deepgram: https://console.deepgram.com"
    echo "  • ElevenLabs: https://elevenlabs.io/api"
    exit 1
fi

echo -e "${GREEN}✓ Environment configured${NC}"

# Check frontend Firebase configuration
FRONTEND_ENV="frontend/.env.local"
if [ ! -f "$FRONTEND_ENV" ]; then
    echo -e "${RED}❌ $FRONTEND_ENV not found${NC}"
    if [ -f frontend/.env.example ]; then
        echo "Creating from template..."
        cp frontend/.env.example "$FRONTEND_ENV"
        echo -e "${YELLOW}⚠️  Please add your Firebase credentials to $FRONTEND_ENV${NC}"
    else
        echo "Missing frontend/.env.example template"
    fi
    exit 1
fi

set -a
source "$FRONTEND_ENV"
set +a

firebase_keys=(
    VITE_FIREBASE_API_KEY
    VITE_FIREBASE_AUTH_DOMAIN
    VITE_FIREBASE_PROJECT_ID
    VITE_FIREBASE_STORAGE_BUCKET
    VITE_FIREBASE_MESSAGING_SENDER_ID
    VITE_FIREBASE_APP_ID
    VITE_FIREBASE_MEASUREMENT_ID
)

firebase_missing=()
for key in "${firebase_keys[@]}"; do
    value="${!key}"
    if [ -z "$value" ] || [[ "$value" == *"your-"* ]] || [[ "$value" == *"your_project"* ]]; then
        firebase_missing+=("$key")
    fi
done

if [ ${#firebase_missing[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing Firebase values in $FRONTEND_ENV:${NC}"
    printf '%s\n' "${firebase_missing[@]}"
    echo ""
    echo "Update these via Firebase Console (see frontend/FIREBASE_SETUP.md)."
    exit 1
fi

echo -e "${GREEN}✓ Frontend Firebase configured${NC}"

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"

# Start services
echo ""
echo "📦 Building and starting services..."
docker compose up --build -d

# Wait for services
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run tests
echo ""
echo "🧪 Running system checks..."
if python3 scripts/test_api.py; then
    echo ""
    echo -e "${GREEN}✅ All systems operational!${NC}"
    echo ""
    echo "📋 Next steps:"
    echo "1. Set up voice samples:"
    echo "   python3 scripts/setup_voice.py --upload --create-voice"
    echo ""
    echo "2. Add persona documents:"
    echo "   python3 scripts/setup_persona.py --reindex"
    echo ""
    echo "3. View logs:"
    echo "   docker compose logs -f"
    echo ""
    echo "4. Access services:"
    echo "   • API: http://localhost:8080"
    echo "   • Trainer: http://localhost:8090"
    echo "   • Database: postgresql://postgres:postgres@localhost:5432/voice"
else
    echo ""
    echo -e "${YELLOW}⚠️  Some services may still be starting${NC}"
    echo "Check logs: docker compose logs"
fi
