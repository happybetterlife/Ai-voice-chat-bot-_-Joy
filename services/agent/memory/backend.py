from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import os
DB_URL=os.getenv('DB_URL','sqlite:///./memory.db')
engine=create_engine(DB_URL, future=True)
SCHEMA_SQL = '''
CREATE TABLE IF NOT EXISTS chat_log (
  id SERIAL PRIMARY KEY,
  room TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS chat_log_room_ts ON chat_log(room, ts);
CREATE TABLE IF NOT EXISTS voices (
  id SERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  provider TEXT NOT NULL,
  voice_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'ready',
  UNIQUE(user_id, provider)
);
CREATE TABLE IF NOT EXISTS persona_index (
  id SERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  backend TEXT NOT NULL DEFAULT 'faiss',
  path TEXT NOT NULL,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''
with engine.begin() as conn:
    for stmt in SCHEMA_SQL.split(';'):
        s = stmt.strip()
        if s: conn.execute(text(s))
def append_message(room, role, content):
    with Session(engine) as s:
        s.execute(text('INSERT INTO chat_log(room,role,content) VALUES (:r,:o,:c)'), {'r':room,'o':role,'c':content}); s.commit()
def load_history(room, limit=12):
    with Session(engine) as s:
        rows=s.execute(text('SELECT role,content FROM chat_log WHERE room=:r ORDER BY ts DESC LIMIT :n'),{'r':room,'n':limit}).all()
        return list(reversed([(r[0],r[1]) for r in rows]))
def set_voice(user_id, provider, voice_id, status='ready'):
    with Session(engine) as s:
        s.execute(text("""INSERT INTO voices(user_id,provider,voice_id,status) VALUES(:u,:p,:v,:s)
ON CONFLICT(user_id,provider) DO UPDATE SET voice_id=:v, status=:s"""), {'u':user_id,'p':provider,'v':voice_id,'s':status}); s.commit()
def get_voice(user_id, provider):
    with Session(engine) as s:
        row=s.execute(text('SELECT voice_id,status FROM voices WHERE user_id=:u AND provider=:p'),{'u':user_id,'p':provider}).first()
        if row: return row[0], row[1]
        return None, None
def set_persona_index(user_id, path, backend='faiss'):
    with Session(engine) as s:
        s.execute(text('INSERT INTO persona_index(user_id,backend,path) VALUES(:u,:b,:p)'),{'u':user_id,'b':backend,'p':path}); s.commit()
