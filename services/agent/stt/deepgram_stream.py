import json, websockets
class DeepgramStreamSTT:
    def __init__(self, api_key: str, sample_rate=16000):
        self.api_key=api_key; self.sample_rate=sample_rate; self.ws=None
    async def __aenter__(self):
        self.ws = await websockets.connect(
            uri=f'wss://api.deepgram.com/v1/listen?model=nova-2&encoding=linear16&sample_rate={self.sample_rate}&punctuate=true&interim_results=true',
            extra_headers={'Authorization': f'Token {self.api_key}'} )
        return self
    async def __aexit__(self, *args):
        if self.ws: await self.ws.close()
    async def send_pcm(self, pcm_bytes: bytes):
        await self.ws.send(pcm_bytes)
    async def recv_transcript(self):
        data = json.loads(await self.ws.recv())
        if 'channel' in data.get('results',{}):
            alts = data['results']['channel']['alternatives']
            if alts:
                return alts[0].get('transcript',''), data['results'].get('is_final', False)
        return '', False
