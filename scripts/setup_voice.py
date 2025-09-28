#!/usr/bin/env python3
"""Utility for preparing voice samples and triggering ElevenLabs cloning."""
from __future__ import annotations

import argparse
import mimetypes
import os
import sys
from pathlib import Path
from typing import Iterable, List

import requests

AUDIO_EXTS = {'.wav', '.mp3', '.m4a'}
DEFAULT_TRAINER_URL = os.getenv('TRAINER_API_URL', 'http://localhost:8090')


def find_audio_files(folder: Path) -> List[Path]:
    return sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_EXTS])


def ensure_voice_dir(user_id: str) -> Path:
    path = Path('data/voice_samples') / user_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def friendly_size(path: Path) -> str:
    size = path.stat().st_size
    units = ['B', 'KB', 'MB', 'GB']
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f}{unit}" if unit != 'B' else f"{size}B"
        size /= 1024
    return f"{size:.1f}TB"


def upload_samples(user_id: str, trainer_url: str, files: Iterable[Path]) -> None:
    url = f"{trainer_url.rstrip('/')}/voice/samples"
    file_handles = []
    payload = []
    try:
        for path in files:
            handle = path.open('rb')
            file_handles.append(handle)
            mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
            payload.append(('files', (path.name, handle, mime)))
        resp = requests.post(url, files=payload, params={'user_id': user_id}, timeout=60)
        resp.raise_for_status()
        saved = resp.json().get('saved')
        print(f"✓ Uploaded samples ({saved} files recorded by trainer service).")
    finally:
        for handle in file_handles:
            handle.close()


def create_voice(user_id: str, voice_name: str, trainer_url: str) -> str:
    url = f"{trainer_url.rstrip('/')}/voice/elevenlabs/create"
    resp = requests.post(url, params={'user_id': user_id, 'voice_name': voice_name}, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    voice_id = data.get('voice_id') or data.get('voice', {}).get('voice_id')
    if not voice_id:
        raise RuntimeError(f"Trainer response missing voice_id: {data}")
    print(f"✓ ElevenLabs voice created: {voice_id}")
    return voice_id


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description='Prepare voice assets and optionally call trainer API endpoints.')
    parser.add_argument('user_id', nargs='?', default='default', help='User identifier used in directory names and trainer API requests.')
    parser.add_argument('--trainer-url', default=DEFAULT_TRAINER_URL, help='Base URL for the trainer service (default: %(default)s).')
    parser.add_argument('--voice-name', help='Name to assign to the ElevenLabs clone (default: voice_<user_id>).')
    parser.add_argument('--upload', action='store_true', help='Upload local audio files to the trainer service.')
    parser.add_argument('--create-voice', action='store_true', help='Request ElevenLabs voice creation after uploading samples.')
    parser.add_argument('--non-interactive', action='store_true', help='Skip interactive confirmations.')
    args = parser.parse_args(argv)

    voice_dir = ensure_voice_dir(args.user_id)
    print(f"Voice sample directory: {voice_dir}")

    audio_files = find_audio_files(voice_dir)
    if audio_files:
        print(f"Found {len(audio_files)} audio file(s):")
        for path in audio_files:
            print(f"  - {path.name} ({friendly_size(path)})")
    else:
        print('No audio files detected. Add clean speech clips (1-2 minutes total recommended).')

    do_upload = args.upload or (not args.non_interactive and _prompt('Upload samples now? [y/N] '))
    if do_upload:
        if not audio_files:
            print('⚠ Nothing to upload. Add audio files first.')
        else:
            try:
                upload_samples(args.user_id, args.trainer_url, audio_files)
            except requests.RequestException as exc:
                print(f"✗ Upload failed: {exc}")
                return 1

    do_create = args.create_voice or (not args.non_interactive and _prompt('Create ElevenLabs voice now? [y/N] '))
    if do_create:
        voice_name = args.voice_name or f"voice_{args.user_id}"
        try:
            create_voice(args.user_id, voice_name, args.trainer_url)
        except requests.RequestException as exc:
            print(f"✗ Voice creation failed: {exc}")
            return 1
        except RuntimeError as exc:
            print(f"✗ {exc}")
            return 1

    print('All done. You can re-run with --upload or --create-voice for subsequent steps.')
    return 0


def _prompt(message: str) -> bool:
    try:
        answer = input(message).strip().lower()
    except EOFError:
        return False
    return answer in {'y', 'yes'}


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
