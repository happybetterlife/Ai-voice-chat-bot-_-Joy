from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic_settings import BaseSettings
from pathlib import Path
import shutil, requests
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

class Settings(BaseSettings):
    ELEVENLABS_API_KEY: str
    DB_URL: str = 'sqlite:///./memory.db'
    MAX_DOC_MB: int = 50
    class Config:
        env_file = '.env'
settings = Settings()

app = FastAPI(title='Trainer API')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
engine = create_engine(settings.DB_URL, future=True)

def set_voice(user_id: str, provider: str, voice_id: str, status: str='ready'):
    with Session(engine) as s:
        s.execute(text("""INSERT INTO voices(user_id,provider,voice_id,status) VALUES(:u,:p,:v,:s)
ON CONFLICT(user_id,provider) DO UPDATE SET voice_id=:v, status=:s"""), {'u':user_id,'p':provider,'v':voice_id,'s':status}); s.commit()

def get_voice(user_id: str, provider: str):
    with Session(engine) as s:
        row=s.execute(text('SELECT voice_id,status FROM voices WHERE user_id=:u AND provider=:p'),{'u':user_id,'p':provider}).first()
        if row: return {'voice_id':row[0],'status':row[1]}
    return {'voice_id':None,'status':None}

@app.post('/voice/samples')
async def upload_samples(user_id: str, samples: List[UploadFile] = File(...)):
    out = Path(f'data/voice_samples/{user_id}'); out.mkdir(parents=True, exist_ok=True)
    for f in samples:
        dest = out / f.filename
        with open(dest, 'wb') as w: shutil.copyfileobj(f.file, w)
    return {'ok': True, 'saved': len(list(out.iterdir()))}

@app.post('/voice/elevenlabs/create')
async def elevenlabs_create(user_id: str, voice_name: str):
    sample_dir = Path(f'data/voice_samples/{user_id}')
    if not sample_dir.exists(): raise HTTPException(400,'No samples uploaded.')
    files=[('files',(p.name, open(p,'rb'), 'application/octet-stream')) for p in sample_dir.glob('*') if p.suffix.lower() in {'.wav','.mp3','.m4a'}]
    if not files: raise HTTPException(400,'No valid audio samples found.')
    headers={'xi-api-key': settings.ELEVENLABS_API_KEY}
    data={'name': voice_name}
    resp=requests.post('https://api.elevenlabs.io/v1/voices/add', headers=headers, files=files, data=data)
    if resp.status_code>=300: raise HTTPException(resp.status_code, f'ElevenLabs error: {resp.text}')
    voice_id = resp.json().get('voice_id') or resp.json().get('voice',{}).get('voice_id')
    if not voice_id: raise HTTPException(500, f'Unexpected provider response: {resp.text}')
    set_voice(user_id, 'elevenlabs', voice_id, 'ready')
    return {'ok': True, 'provider': 'elevenlabs', 'voice_id': voice_id}

@app.get('/voice/get')
def voice_get(user_id: str, provider: str = 'elevenlabs'):
    return get_voice(user_id, provider)

@app.post('/persona/upload')
async def persona_upload(user_id: str, files: List[UploadFile] = File(...)):
    root = Path(f'data/persona/{user_id}'); root.mkdir(parents=True, exist_ok=True)
    for f in files:
        dest = root / f.filename
        with open(dest, 'wb') as w: shutil.copyfileobj(f.file, w)
    return {'ok': True, 'user_id': user_id}

@app.post('/persona/reindex')
def persona_reindex(user_id: str):
    import subprocess, sys
    corpus=f'data/persona/{user_id}'; out=f'data/indexes/{user_id}'
    Path(corpus).mkdir(parents=True, exist_ok=True); Path(out).mkdir(parents=True, exist_ok=True)
    result = subprocess.run([sys.executable, 'services/agent/rag/indexer.py', '--corpus', corpus, '--out', out], capture_output=True, text=True)
    if result.returncode != 0: raise HTTPException(500, f'Indexing failed: {result.stderr}')
    with Session(engine) as s:
        s.execute(text('INSERT INTO persona_index(user_id,backend,path) VALUES(:u,:b,:p)'), {'u':user_id,'b':'faiss','p':out}); s.commit()
    return {'ok': True, 'index_path': out, 'log': result.stdout}
