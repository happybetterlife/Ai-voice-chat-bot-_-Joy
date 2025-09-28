import asyncio, os, requests
from livekit import rtc
from config import settings
from vad import SileroVAD
from stt.deepgram_stream import DeepgramStreamSTT
from tts.eleven_stream import ElevenStreamTTS
from llm.openai_chat import ChatLLM
from memory import backend as mem
from rag.query import RAG
SYSTEM=settings.AGENT_SYSTEM_PROMPT

def resolve_voice_for_user(user_id: str) -> str:
    if settings.AGENT_VOICE_ID: return settings.AGENT_VOICE_ID
    voice_id, status = mem.get_voice(user_id, settings.AGENT_VOICE_PROVIDER)
    if voice_id and status=='ready': return voice_id
    return settings.DEFAULT_VOICE_ID

async def join_room(identity: str, name: str|None=None):
    r=requests.post('http://api:8080/token', json={'identity':identity,'name':name or identity}); r.raise_for_status(); data=r.json()
    room=rtc.Room(); await room.connect(data['url'], data['token']); return room

async def speak_text(text: str, tts_task_holder: dict, voice_id: str):
    if tts_task_holder.get('task') and not tts_task_holder['task'].done(): tts_task_holder['task'].cancel()
    async def _run():
        async with ElevenStreamTTS(settings.ELEVENLABS_API_KEY, voice_id) as tts:
            await tts.send_text(text)
    task=asyncio.create_task(_run()); tts_task_holder['task']=task; await task

async def handle_participant(room: rtc.Room, user_id: str):
    llm=ChatLLM(api_key=settings.OPENAI_API_KEY)
    base_dir = f'data/indexes/{user_id}' if os.path.exists(f'data/indexes/{user_id}') else 'data/indexes/default'
    rag=RAG(backend=settings.RAG_BACKEND, base_dir=base_dir)
    history=mem.load_history(room.name, limit=settings.HISTORY_RELOAD_TURNS)
    messages=[{'role':'system','content':SYSTEM}] + [{'role':r,'content':c} for r,c in history]
    greet='Hello! I’m ready. Start speaking whenever you like.'
    messages.append({'role':'assistant','content':greet}); mem.append_message(room.name,'assistant',greet)
    tts_task_holder={'task': None}; voice_id=resolve_voice_for_user(user_id)
    audio_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=32)
    def on_track(track_pub, _):
        if isinstance(track_pub.track, rtc.RemoteAudioTrack):
            track_pub.track.add_audio_frame_received(lambda f: audio_queue.put_nowait(f.data))
    room.on('track_subscribed', on_track)
    async with DeepgramStreamSTT(settings.DEEPGRAM_API_KEY) as stt:
        speaking=False
        while True:
            pcm = await audio_queue.get(); await stt.send_pcm(pcm)
            if not speaking:
                speaking=True
                if tts_task_holder.get('task') and not tts_task_holder['task'].done(): tts_task_holder['task'].cancel()
            text, is_final = await stt.recv_transcript()
            if not text: continue
            if is_final:
                ctx = rag.topk(text, k=4); context_blob='\n\n'.join([c[0] for c in ctx])
                turn = messages + [{'role':'user','content':text},{'role':'system','content':f'Relevant context (non-user visible)\n---\n{context_blob}'}]
                reply = llm.complete(turn)
                mem.append_message(room.name,'user',text); mem.append_message(room.name,'assistant',reply)
                messages += [{'role':'user','content':text},{'role':'assistant','content':reply}]
                await speak_text(reply, tts_task_holder, voice_id); speaking=False

async def main():
    user_id=os.getenv('DEMO_USER_ID','joyce'); room=await join_room(identity=user_id)
    try:
        await handle_participant(room, user_id=user_id)
    finally:
        await room.disconnect()

if __name__=='__main__':
    asyncio.run(main())
