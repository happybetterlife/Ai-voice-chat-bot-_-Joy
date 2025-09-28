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
  const [identity] = useState('user');
  const [loading, setLoading] = useState(false);
  const [showVoiceCloning, setShowVoiceCloning] = useState(false);

  const connect = async () => {
    setLoading(true);

    try {
      const res = await axios.post(`${import.meta.env.VITE_API_BASE}/token`, {
        identity,
        name: `Voice Agent Session`
      });

      if (res.data.token && res.data.url) {
        setToken(res.data.token);
        setUrl(res.data.url);
      }
    } catch (err: any) {
      console.error('Connection failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const disconnect = () => {
    setToken(undefined);
    setUrl(undefined);
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
                <h2>Voice Agent</h2>
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
      <Navigation />
      
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <div className="hero-badge">
              <span>Try Now</span>
            </div>
            <h1>Meet AI Voice Agent</h1>
            <p className="hero-subtitle">
              Your AI voice assistant powered by advanced technology. Whether you're starting your journey or advancing your career, your AI voice agent is here to guide you.
            </p>
            <div className="hero-actions">
              <button 
                onClick={connect}
                disabled={loading || !identity}
                className="btn btn-primary btn-large"
              >
                {loading ? 'Connecting...' : 'Say Hello'}
              </button>
              <button 
                onClick={() => setShowVoiceCloning(true)}
                className="btn btn-secondary btn-large"
              >
                Clone Your Voice
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features">
        <div className="container">
          <div className="features-header">
            <h2>Your AI Learning Partner</h2>
            <p>Advanced voice interaction capabilities for personalized assistance</p>
          </div>
          
          <div className="features-grid">
            <div className="feature-item">
              <h3>Technical mentorship</h3>
              <p>Navigate complex AI concepts with personalized explanations tailored to your knowledge level</p>
            </div>
            <div className="feature-item">
              <h3>Project guidance</h3>
              <p>Discuss implementation challenges and receive conceptual direction for your technical projects</p>
            </div>
            <div className="feature-item">
              <h3>Career development</h3>
              <p>Get strategic advice on learning paths, portfolio projects, and industry opportunities</p>
            </div>
            <div className="feature-item">
              <h3>Course recommendations</h3>
              <p>Discover the right educational resources based on your background and goals</p>
            </div>
          </div>
        </div>
      </section>

      {/* Why Section */}
      <section className="why-section">
        <div className="container">
          <h2>Why VoiceAgent?</h2>
          <p>VoiceAgent brings you an AI voice assistant backed by advanced technology and expertise.</p>
          
          <div className="why-grid">
            <div className="why-item">
              <h3>Authentic</h3>
              <p>Trained on advanced knowledge, teaching style, and problem-solving approach to deliver a genuine mentorship experience</p>
            </div>
            <div className="why-item">
              <h3>Adaptive</h3>
              <p>Tailors conversations to your skill level, remembering your progress and building on previous discussions</p>
            </div>
            <div className="why-item">
              <h3>Accessible</h3>
              <p>Available anytime through voice calls, providing immediate guidance when you need it most</p>
            </div>
          </div>
        </div>
      </section>

      {/* AI In Own Words Section */}
      <section className="ai-words">
        <div className="container">
          <div className="ai-content">
            <h2>AI Voice Agent, In Their Own Words</h2>
            <p>Chat with your AI voice agent directly. Get personalized mentorship, technical guidance, and career advice.</p>
            
            <div className="conversation-topics">
              <h3>Connect through voice</h3>
              <p>Engage in natural conversations about:</p>
              <div className="topics-grid">
                <div className="topic">Implementation challenges</div>
                <div className="topic">Learning strategies</div>
                <div className="topic">Career decisions</div>
                <div className="topic">Technical concepts</div>
                <div className="topic">Project feedback</div>
              </div>
            </div>
            
            <button 
              onClick={connect}
              disabled={loading || !identity}
              className="btn btn-primary btn-large"
            >
              Try now
            </button>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="testimonials">
        <div className="container">
          <h2>Community testimonials</h2>
          
          <div className="testimonials-grid">
            <div className="testimonial">
              <div className="testimonial-content">
                <p>"Before this product, not many people have had the chance to be mentored by an AI voice agent. The advice and suggestions are very well researched and I can see this tool helping many developers shift their careers."</p>
              </div>
              <div className="testimonial-author">
                <strong>Misha</strong>
                <span>AI Researcher</span>
              </div>
            </div>
            
            <div className="testimonial">
              <div className="testimonial-content">
                <p>"As a Product Manager, I love discussing the latest AI news with the voice agent. The insights into the evolving landscape of AI have been incredibly inspiring and have deepened my understanding of the field."</p>
              </div>
              <div className="testimonial-author">
                <strong>Rita</strong>
                <span>Product Manager</span>
              </div>
            </div>
            
            <div className="testimonial">
              <div className="testimonial-content">
                <p>"Having in-depth conversations with the AI voice agent on specific topics is a game changer. I feel like I am having calls during private office hours."</p>
              </div>
              <div className="testimonial-author">
                <strong>James</strong>
                <span>Software Engineer, Student</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to get started?</h2>
            <p>Join our community and start your AI voice journey today.</p>
            <div className="cta-actions">
              <button 
                onClick={connect}
                disabled={loading || !identity}
                className="btn btn-primary btn-large"
              >
                {loading ? 'Connecting...' : 'Start Learning'}
              </button>
              <button 
                onClick={() => setShowVoiceCloning(true)}
                className="btn btn-secondary btn-large"
              >
                Join Discord community
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <span>© 2025 VoiceAgent. All rights reserved</span>
            </div>
            <div className="footer-links">
              <a href="#">Terms Of Service</a>
              <a href="#">Privacy Policy</a>
            </div>
          </div>
        </div>
      </footer>

      {/* Voice Cloning Modal */}
      <VoiceCloningModal 
        isOpen={showVoiceCloning} 
        onClose={() => setShowVoiceCloning(false)} 
      />
    </div>
  );
}

export default App
