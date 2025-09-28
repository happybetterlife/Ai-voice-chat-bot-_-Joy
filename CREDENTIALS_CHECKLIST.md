# 🔑 API Credentials Checklist

Before running the voice agent system, you need to configure API keys in both frontend and backend.

## Backend Configuration (`.env`)

Currently **EMPTY** - Fill these in before starting services:

### Required API Keys

1. **LiveKit** - Real-time communication
   ```env
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_secret
   ```
   📍 Get from: https://cloud.livekit.io

2. **OpenAI** - LLM for conversation
   ```env
   OPENAI_API_KEY=sk-...
   ```
   📍 Get from: https://platform.openai.com/api-keys

3. **Deepgram** - Speech-to-Text
   ```env
   DEEPGRAM_API_KEY=...
   ```
   📍 Get from: https://console.deepgram.com

4. **ElevenLabs** - Text-to-Speech
   ```env
   ELEVENLABS_API_KEY=...
   ```
   📍 Get from: https://elevenlabs.io/api

### Pre-configured Settings
```env
AGENT_VOICE_PROVIDER=elevenlabs
DEFAULT_VOICE_ID=Rachel
RAG_BACKEND=faiss
DB_URL=postgresql+psycopg2://postgres:postgres@db:5432/voice
```

## Frontend Configuration (`frontend/.env.local`)

✅ **CONFIGURED** - Firebase keys are already set

## 🚨 Critical Steps Before Testing

### 1. Fill Backend `.env`
```bash
# Copy template and edit
cp .env.example .env
# Edit .env with your actual API keys
```

### 2. Verify Frontend Keys
```bash
# Should exist with Firebase config
cat frontend/.env.local
```

### 3. Test Configuration
```bash
# Quick validation
python3 scripts/test_api.py
```

## 🧪 End-to-End Test Workflow

Once both files are configured:

```bash
# 1. Start backend services
docker compose up --build

# 2. Start frontend (separate terminal)
cd frontend && npm run dev

# 3. Test the system
# - Open http://localhost:5173
# - Enter user ID (e.g., "default")
# - Click "Start Voice Session"
# - Allow microphone access
# - Speak and verify AI response
```

## 🔍 Troubleshooting

### Service Won't Start
- Check all API keys are filled in `.env`
- Verify no extra spaces or quotes around keys
- Check Docker logs: `docker compose logs [service]`

### No Voice Response
- Verify ElevenLabs API key and quota
- Check if voice is created: `python3 scripts/setup_voice.py`
- Monitor agent logs: `docker compose logs agent`

### Connection Failed
- Verify LiveKit credentials
- Check network connectivity
- Ensure CORS is configured properly

## 💡 Pro Tips

1. **Use environment-specific files**:
   - `.env.local` for local development
   - `.env.production` for production deployment

2. **API Key Security**:
   - Never commit real keys to version control
   - Use separate keys for dev/staging/production
   - Monitor usage in respective dashboards

3. **Cost Management**:
   - Set usage limits in OpenAI/Deepgram/ElevenLabs dashboards
   - Monitor costs regularly
   - Use cheaper models for development/testing

---

**⚠️ IMPORTANT**: Without proper API keys, the services will fail to start or function correctly!