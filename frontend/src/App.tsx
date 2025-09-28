import { useState } from 'react';
import axios from 'axios';
import {
  LiveKitRoom,
  AudioTrack,
  RoomAudioRenderer,
  useConnectionState,
  useTracks
} from '@livekit/components-react';
import '@livekit/components-styles';
import './App.css';
import { Track } from 'livekit-client';

// Navigation Component
function Navigation() {
  return (
    <nav className="nav">
      <div className="nav-container">
        <div className="nav-brand">
          <span className="brand-text">VoiceAgent</span>
        </div>
        <div className="nav-links">
          <a href="#features" className="nav-link">Features</a>
          <a href="#testimonials" className="nav-link">Testimonials</a>
          <button className="nav-cta">Try Now</button>
        </div>
      </div>
    </nav>
  );
}

// Voice Cloning Modal Component
function VoiceCloningModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [files, setFiles] = useState<FileList | null>(null);
  const [voiceName, setVoiceName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [message, setMessage] = useState('');

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files);
  };

  const uploadSamples = async () => {
    if (!files || files.length === 0) return;
    
    setUploading(true);
    setMessage('');
    
    try {
      const formData = new FormData();
      Array.from(files).forEach(file => {
        formData.append('samples', file);
      });
      
      const response = await axios.post(
        `${import.meta.env.VITE_API_BASE?.replace(':8080', ':8090')}/voice/samples?user_id=default`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      
      setMessage(`✅ ${response.data.saved} files uploaded successfully!`);
    } catch (error) {
      setMessage('❌ Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const createVoice = async () => {
    if (!voiceName) return;
    
    setCreating(true);
    setMessage('');
    
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_BASE?.replace(':8080', ':8090')}/voice/elevenlabs/create?user_id=default&voice_name=${voiceName}`
      );
      
      setMessage(`✅ Voice "${voiceName}" created successfully! Voice ID: ${response.data.voice_id}`);
    } catch (error) {
      setMessage('❌ Voice creation failed. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Clone Your Voice</h3>
          <button onClick={onClose} className="modal-close">×</button>
        </div>
        <div className="modal-body">
          <p>Upload audio samples to create your personalized AI voice</p>
          
          <div className="form-group">
            <input
              type="file"
              multiple
              accept=".wav,.mp3,.m4a"
              onChange={handleFileChange}
              className="file-input"
            />
            <button 
              onClick={uploadSamples} 
              disabled={!files || uploading}
              className="btn btn-secondary"
            >
              {uploading ? 'Uploading...' : 'Upload Samples'}
            </button>
          </div>
          
          <div className="form-group">
            <input
              type="text"
              placeholder="Enter voice name"
              value={voiceName}
              onChange={(e) => setVoiceName(e.target.value)}
              className="text-input"
            />
            <button 
              onClick={createVoice} 
              disabled={!voiceName || creating}
              className="btn btn-primary"
            >
              {creating ? 'Creating...' : 'Create Voice'}
            </button>
          </div>
          
          {message && <div className="message">{message}</div>}
        </div>
      </div>
    </div>
  );
}

// Room Content Component
function RoomContent() {
  const connectionState = useConnectionState();
  const tracks = useTracks([Track.Source.Microphone]);

  return (
    <div className="room-content">
      <div className="status-indicator">
        <div className={`status-dot ${connectionState === 'connected' ? 'connected' : 'disconnected'}`} />
        <span>{connectionState === 'connected' ? 'Connected' : connectionState}</span>
      </div>

      <div className="audio-section">
        <RoomAudioRenderer />
        <div className="audio-info">
          <h3>Active Audio Streams</h3>
          {tracks.length === 0 && <p>No audio tracks detected</p>}
          {tracks.map((track) => (
            <AudioTrack key={track.participant.identity} {...track} />
          ))}
        </div>
      </div>

      <div className="listening-indicator">
        <div className="pulse-animation"></div>
        <p>🎤 AI Voice Agent is listening...</p>
      </div>
    </div>
  );
}

// Main App Component
function App() {
  const [token, setToken] = useState<string>();
  const [url, setUrl] = useState<string>();
  const [identity, setIdentity] = useState('user');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();
  const [showVoiceCloning, setShowVoiceCloning] = useState(false);

  const connect = async () => {
    setLoading(true);
    setError(undefined);

    try {
      const res = await axios.post(`${import.meta.env.VITE_API_BASE}/token`, {
        identity,
        name: `Voice Agent Session`
      });

      if (res.data.token && res.data.url) {
        setToken(res.data.token);
        setUrl(res.data.url);
      } else {
        setError('Invalid response from server');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Connection failed');
    } finally {
      setLoading(false);
    }
  };

  const disconnect = () => {
    setToken(undefined);
    setUrl(undefined);
    setError(undefined);
  };

  // Voice Chat Session View
  if (token && url) {
    return (
      <div className="app">
        <LiveKitRoom
          token={token}
          serverUrl={url}
          connect={true}
          audio={true}
          video={false}
          onDisconnected={disconnect}
          options={{
            adaptiveStream: true,
            dynacast: true,
          }}
        >
          <div className="chat-interface">
            <header className="chat-header">
              <div className="header-content">
                <h2>🎙️ Voice Agent Pro</h2>
                <button onClick={disconnect} className="btn btn-outline">
                  Disconnect
                </button>
              </div>
            </header>
            
            <main className="chat-main">
              <RoomContent />
            </main>
          </div>
        </LiveKitRoom>
      </div>
    );
  }

  // Landing Page View
  return (
    <div className="app">
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <h1>Meet Your AI Voice Assistant</h1>
            <p className="hero-subtitle">
              Experience the future of voice interaction with our advanced AI voice agent. 
              Clone your voice, have natural conversations, and get personalized assistance.
            </p>
            
            <div className="hero-actions">
              <button 
                onClick={() => setShowVoiceCloning(true)}
                className="btn btn-secondary btn-large"
              >
                Clone Your Voice
              </button>
              <button 
                onClick={connect}
                disabled={loading || !identity}
                className="btn btn-primary btn-large"
              >
                {loading ? 'Connecting...' : 'Start Voice Chat'}
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <h2 className="text-center mb-8">Why Choose Our Voice Agent?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>Personalized Voice</h3>
              <p>Clone your own voice for a truly personalized AI experience</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🧠</div>
              <h3>Intelligent Conversations</h3>
              <p>Advanced AI powered by cutting-edge language models</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Real-time Processing</h3>
              <p>Low-latency voice processing for natural conversations</p>
            </div>
          </div>
        </div>
      </section>

      {/* Voice Cloning Modal */}
      {showVoiceCloning && (
        <div className="modal-overlay" onClick={() => setShowVoiceCloning(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Voice Cloning</h3>
              <button 
                onClick={() => setShowVoiceCloning(false)}
                className="modal-close"
              >
                ×
              </button>
            </div>
            <VoiceCloningPanel />
          </div>
        </div>
      )}

      {/* Connection Form */}
      <section className="connection-form">
        <div className="container">
          <div className="form-card">
            <h3>Quick Start</h3>
            <div className="form-group">
              <label>User ID</label>
              <input
                type="text"
                value={identity}
                onChange={e => setIdentity(e.target.value)}
                placeholder="Enter your user ID"
                disabled={loading}
                className="text-input"
              />
            </div>
            
            {error && <div className="error-message">{error}</div>}
            
            <div className="requirements">
              <h4>📋 Requirements:</h4>
              <ul>
                <li>Microphone access required</li>
                <li>Voice agent must be running</li>
                <li>Stable internet connection</li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default App
