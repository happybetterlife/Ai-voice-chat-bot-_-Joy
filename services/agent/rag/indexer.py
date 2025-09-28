from sentence_transformers import SentenceTransformer
import faiss, json
from pathlib import Path
from .loaders import load_texts
MODEL='sentence-transformers/all-MiniLM-L6-v2'

def chunk(text, size=700, overlap=120):
    out=[]; i=0
    while i<len(text): out.append(text[i:i+size]); i+= size-overlap
    return out

def build_faiss(corpus_dir: str, out_dir: str):
    outp=Path(out_dir); outp.mkdir(parents=True, exist_ok=True)
    model=SentenceTransformer(MODEL)
    texts=[]
    for t in load_texts(Path(corpus_dir)): texts.extend(chunk(t))
    embs=model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    index=faiss.IndexFlatIP(embs.shape[1]); faiss.normalize_L2(embs); index.add(embs.astype('float32'))
    faiss.write_index(index, str(outp/'faiss.index'))
    (outp/'meta.json').write_text(json.dumps({'texts':texts}, ensure_ascii=False))
    print(f'Indexed {len(texts)} chunks → {outp}')
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('--corpus', default='data/persona/default'); ap.add_argument('--out', default='data/indexes/default'); args=ap.parse_args(); build_faiss(args.corpus, args.out)
