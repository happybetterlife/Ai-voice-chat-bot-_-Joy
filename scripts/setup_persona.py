#!/usr/bin/env python3
"""Helper for managing persona documents and triggering reindexing."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Iterable, List

import requests

SUPPORTED_SUFFIXES = {'.pdf', '.txt', '.md'}
DEFAULT_TRAINER_URL = os.getenv('TRAINER_API_URL', 'http://localhost:8090')


def ensure_persona_dir(user_id: str) -> Path:
    path = Path('data/persona') / user_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_documents(folder: Path) -> List[Path]:
    return sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES])


def friendly_size(path: Path) -> str:
    size = path.stat().st_size
    units = ['B', 'KB', 'MB', 'GB']
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f}{unit}" if unit != 'B' else f"{size}B"
        size /= 1024
    return f"{size:.1f}TB"


def reindex_persona(user_id: str, trainer_url: str, show_log: bool = False) -> bool:
    url = f"{trainer_url.rstrip('/')}/persona/reindex"
    try:
        resp = requests.post(url, params={'user_id': user_id}, timeout=120)
        resp.raise_for_status()
    except requests.ConnectionError:
        print('✗ Cannot reach trainer API. Start it with `docker compose up trainer`.')
        return False
    except requests.RequestException as exc:
        print(f'✗ Reindex request failed: {exc}')
        return False

    data = resp.json()
    print('✓ Persona index rebuilt.')
    print(f"  - Backend: {data.get('backend', 'faiss')}")
    print(f"  - Index path: {data.get('index_path', f'data/indexes/{user_id}')}" )
    if show_log:
        print('\n--- Index Log ---')
        print(data.get('log', '').strip())
        print('-----------------')
    return True


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description='Prepare persona docs and trigger indexing via trainer API.')
    parser.add_argument('user_id', nargs='?', default='default', help='User identifier for persona assets.')
    parser.add_argument('--trainer-url', default=DEFAULT_TRAINER_URL, help='Trainer service base URL (default: %(default)s).')
    parser.add_argument('--reindex', action='store_true', help='Trigger indexing immediately without prompting.')
    parser.add_argument('--show-log', action='store_true', help='Print indexing log returned by the trainer service.')
    parser.add_argument('--non-interactive', action='store_true', help='Do not ask for confirmation before reindexing.')
    args = parser.parse_args(argv)

    persona_dir = ensure_persona_dir(args.user_id)
    print(f"Persona directory: {persona_dir}")

    docs = list_documents(persona_dir)
    if docs:
        print(f"Found {len(docs)} supported document(s):")
        for path in docs:
            print(f"  - {path.name} ({friendly_size(path)})")
    else:
        print('No persona documents detected. Add PDF/TXT/MD files describing the persona.')

    should_reindex = args.reindex or (docs and not args.non_interactive and _prompt('Reindex now? [y/N] '))
    if should_reindex:
        reindex_persona(args.user_id, args.trainer_url, args.show_log)
    else:
        if not docs:
            print('\nNext steps: populate the directory then re-run with --reindex to build embeddings.')
        else:
            print('\nRe-run with --reindex when you are ready to refresh the index.')

    return 0


def _prompt(message: str) -> bool:
    try:
        answer = input(message).strip().lower()
    except EOFError:
        return False
    return answer in {'y', 'yes'}


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
