# Voice Agent Frontend

React-based web interface for the Voice Agent Pro system with LiveKit integration.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:5173
```

## Features

- 🎤 Real-time voice communication via LiveKit
- 🔊 AI voice agent with custom ElevenLabs voices
- 👤 User-specific persona support
- 🎨 Modern, responsive UI

## Development

```bash
# Start backend services first
docker compose up

# Then start frontend
npm run dev
```

## Production Build

```bash
npm run build
npm run preview
```

## Configuration

Create a `.env` file:
```env
VITE_API_BASE=http://localhost:8080
```

## Deployment

### Static Hosting
```bash
npm run build
# Deploy dist/ folder to Vercel, Netlify, etc.
```

### Docker
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```
