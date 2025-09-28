import { useState, useEffect } from 'react';
import {
  useLocalParticipant,
  useTracks,
} from '@livekit/components-react';
import { Track } from 'livekit-client';

export function VoiceControls() {
  const [isMuted, setIsMuted] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const { localParticipant } = useLocalParticipant();
  const tracks = useTracks([Track.Source.Microphone]);

  useEffect(() => {
    if (tracks.length > 0) {
      setIsListening(true);
    }
  }, [tracks]);

  const toggleMute = async () => {
    if (!localParticipant) return;

    if (isMuted) {
      await localParticipant.setMicrophoneEnabled(true);
      setIsMuted(false);
    } else {
      await localParticipant.setMicrophoneEnabled(false);
      setIsMuted(true);
    }
  };

  return (
    <div className="voice-controls">
      <button
        className={`mute-button ${isMuted ? 'muted' : 'active'}`}
        onClick={toggleMute}
        aria-label={isMuted ? 'Unmute' : 'Mute'}
      >
        {isMuted ? '🔇' : '🎤'} {isMuted ? 'Unmuted' : 'Muted'}
      </button>

      <div className="audio-indicator">
        {isListening && !isMuted && (
          <div className="listening-indicator">
            <span className="pulse-dot" />
            <span>Listening...</span>
          </div>
        )}
      </div>
    </div>
  );
}