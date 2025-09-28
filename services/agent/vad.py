import torch, torchaudio
class SileroVAD:
    def __init__(self, sampling_rate=16000, threshold=0.5):
        self.model, self.utils = torch.hub.load('snakers4/silero-vad','silero_vad',force_reload=False)
        (self.get_speech_timestamps, _, self.read_audio, *_ ) = self.utils
        self.sr = sampling_rate
        self.threshold = threshold
    def is_speech(self, audio):
        with torch.no_grad():
            probs = self.model(audio, self.sr).item()
        return probs > self.threshold, probs
