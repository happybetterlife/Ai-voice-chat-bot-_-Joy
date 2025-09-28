from pathlib import Path
from pypdf import PdfReader
def load_texts(corpus_dir: Path):
    texts=[]
    for p in corpus_dir.rglob('*'):
        if p.suffix.lower() in {'.txt','.md'}:
            texts.append(p.read_text(encoding='utf-8', errors='ignore'))
        elif p.suffix.lower()=='.pdf':
            reader=PdfReader(str(p)); parts=[page.extract_text() or '' for page in reader.pages]
            texts.append('\n'.join(parts))
    return texts
