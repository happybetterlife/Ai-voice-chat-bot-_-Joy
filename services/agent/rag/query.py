import json, faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer
MODEL='sentence-transformers/all-MiniLM-L6-v2'
class RAG:
    def __init__(self, backend='faiss', base_dir='data/indexes/default', pinecone_conf=None):
        self.backend=backend; self.base_dir=Path(base_dir); self.model=SentenceTransformer(MODEL)
        if backend=='faiss':
            self.index=faiss.read_index(str(self.base_dir/'faiss.index'))
            self.meta=json.loads((self.base_dir/'meta.json').read_text())
        elif backend=='pinecone':
            import pinecone; pinecone.init(api_key=pinecone_conf['api_key'], environment=pinecone_conf['env']); self.index=pinecone.Index(pinecone_conf['index'])
        else: raise ValueError('backend must be faiss or pinecone')
    def topk(self, query: str, k=4):
        q=self.model.encode([query], convert_to_numpy=True); faiss.normalize_L2(q)
        if self.backend=='faiss':
            D,I=self.index.search(q.astype('float32'), k); texts=[self.meta['texts'][i] for i in I[0]]; return list(zip(texts, D[0].tolist()))
        else:
            res=self.index.query(vector=q[0].tolist(), top_k=k, include_metadata=True); return [(m['metadata']['text'], m['score']) for m in res['matches']]
