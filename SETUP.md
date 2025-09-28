# Voice Agent Setup Guide

## Prerequisites

- Docker & Docker Compose
- Python 3.8+
- API Keys from:
  - [LiveKit Cloud](https://cloud.livekit.io)
  - [OpenAI](https://platform.openai.com/api-keys)
  - [Deepgram](https://console.deepgram.com)
  - [ElevenLabs](https://elevenlabs.io/api)

## Quick Start

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env and add your API keys

# 2. Run quick start script
chmod +x scripts/quick_start.sh
./scripts/quick_start.sh

# 3. Set up voice cloning
chmod +x scripts/setup_voice.py
./scripts/setup_voice.py default --upload --create-voice

# 4. Set up persona
chmod +x scripts/setup_persona.py
./scripts/setup_persona.py default --reindex
```

## Manual Setup

### 1. Environment Configuration

Fill in your `.env` file with:
```env
LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_secret
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...
ELEVENLABS_API_KEY=...
```

### 2. Start Services

```bash
# Start all services
docker compose up --build

# Or start individually
docker compose up db       # Database
docker compose up trainer  # Voice training API
docker compose up api      # Main API
docker compose up agent    # Voice agent
```

### 3. Voice Setup

Place audio samples in `data/voice_samples/[user_id]/`:
- Format: WAV, MP3, or M4A
- Duration: 1-2 minutes of clear speech
- Quality: Good audio without background noise

Then create the voice:
```bash
python3 scripts/setup_voice.py [user_id] --upload --create-voice
```

### 4. Persona Setup

Add documents to `data/persona/[user_id]/`:
- Formats: PDF, TXT, MD
- Content: Character background, speaking style, knowledge base

Then index:
```bash
python3 scripts/setup_persona.py [user_id] --reindex
```

### 5. Test the System

```bash
python3 scripts/test_api.py --user-id [user_id]
```

## Multi-User Setup

For multiple users, create separate directories:

```bash
# For each user
USER_ID="user123"

# Voice samples
mkdir -p data/voice_samples/$USER_ID
# Add audio files...

# Persona documents
mkdir -p data/persona/$USER_ID
# Add documents...

# Process
./scripts/setup_voice.py $USER_ID --upload --create-voice
./scripts/setup_persona.py $USER_ID --reindex
```

## Troubleshooting

### Services won't start
- Check Docker is running
- Verify all API keys in `.env`
- Check logs: `docker compose logs [service]`

### Voice cloning fails
- Ensure audio files are in correct format
- Check ElevenLabs API key and quota
- Verify trainer service is running

### Persona indexing fails
- Check document formats (PDF/TXT/MD only)
- Verify trainer service is running
- Check `data/indexes/[user_id]/` for index files

### Database issues
```bash
# Reset database
docker compose down -v
docker compose up db
```

## Production Considerations

1. **Security**: Never commit `.env` file
2. **Performance**: Adjust worker counts in `docker-compose.yml`
3. **Storage**: Monitor `data/` directory size
4. **Monitoring**: Set up logging aggregation
5. **Backup**: Regular database and index backups

## API Endpoints

- **Main API** (port 8080)
  - `GET /health` - Health check
  - `POST /token` - Generate LiveKit token (JSON body with `identity` field)

- **Trainer API** (port 8090)
  - `POST /voice/samples` - Upload voice samples
  - `POST /voice/elevenlabs/create` - Create voice
  - `GET /voice/get` - Check voice status
  - `POST /persona/reindex` - Reindex persona documents

## Support

- Check service logs: `docker compose logs -f [service]`
- Test individual services: `python3 scripts/test_api.py`
- Database console: `docker compose exec db psql -U postgres -d voice`