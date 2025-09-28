import json, websockets
class ElevenStreamTTS:
    def __init__(self, api_key: str, voice_id: str, model='eleven_multilingual_v2'):
        self.api_key=api_key; self.voice_id=voice_id; self.model=model; self.ws=None
    async def __aenter__(self):
        self.ws = await websockets.connect(
            f'wss://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream-input?model_id={self.model}',
            extra_headers={'xi-api-key': self.api_key})
        await self.ws.send(json.dumps({'text':'','voice_settings':{'stability':0.4,'similarity_boost':0.7}}))
        return self
    async def __aexit__(self, *args):
        if self.ws: await self.ws.close()
    async def send_text(self, text: str, flush=True):
        await self.ws.send(json.dumps({'text': text}))
        if flush: await self.ws.send(json.dumps({'flush': True}))
