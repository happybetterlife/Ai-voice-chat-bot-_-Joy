from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from livekit_token import create_token
from models import TokenReq, TokenResp
app = FastAPI(title='Voice Agent API')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
@app.get('/health')
def health():
    return {'ok': True}
@app.post('/token', response_model=TokenResp)
def mint_token(req: TokenReq):
    if not req.identity:
        raise HTTPException(400, 'identity required')
    token = create_token(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET, req.identity)
    return TokenResp(url=settings.LIVEKIT_URL, token=token)
