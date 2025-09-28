#!/usr/bin/env python3
"""Smoke tests for the Voice Agent API and trainer services."""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests

DEFAULT_API_URL = 'http://localhost:8080'
DEFAULT_TRAINER_URL = 'http://localhost:8090'


@dataclass
class CheckResult:
    ok: bool
    detail: str
    payload: Optional[dict] = None


def check_api_health(api_url: str) -> CheckResult:
    try:
        resp = requests.get(f"{api_url}/health", timeout=5)
        if resp.status_code == 200 and resp.json().get('ok') is True:
            return CheckResult(True, 'API health endpoint responded.')
        return CheckResult(False, f"Unexpected response: {resp.status_code} {resp.text}")
    except requests.ConnectionError:
        return CheckResult(False, 'Cannot reach API. Start it with `docker compose up api`.')
    except requests.RequestException as exc:
        return CheckResult(False, f"API health request failed: {exc}")


def check_token(api_url: str, user_id: str, room_name: str) -> CheckResult:
    payload = {'identity': user_id, 'name': room_name}
    try:
        resp = requests.post(f"{api_url}/token", json=payload, timeout=10)
        if resp.status_code != 200:
            return CheckResult(False, f"Token endpoint returned {resp.status_code}: {resp.text}")
        data = resp.json()
        token = data.get('token')
        url = data.get('url')
        if token and url:
            return CheckResult(True, f"Token issued (len={len(token)}) for identity '{user_id}'.", {'token': token, 'url': url})
        return CheckResult(False, f"Token response missing fields: {data}")
    except requests.ConnectionError:
        return CheckResult(False, 'Cannot reach API token endpoint.')
    except requests.RequestException as exc:
        return CheckResult(False, f"Token request failed: {exc}")


def check_trainer_voice(trainer_url: str, user_id: str) -> CheckResult:
    try:
        resp = requests.get(f"{trainer_url}/voice/get", params={'user_id': user_id}, timeout=10)
        if resp.status_code != 200:
            return CheckResult(False, f"/voice/get returned {resp.status_code}: {resp.text}")
        data = resp.json()
        voice_id = data.get('voice_id')
        status = data.get('status')
        if voice_id:
            return CheckResult(True, f"Voice '{voice_id}' found (status={status}).", data)
        return CheckResult(False, f"No voice registered for '{user_id}'.", data)
    except requests.ConnectionError:
        return CheckResult(False, 'Cannot reach trainer service. Start it with `docker compose up trainer`.')
    except requests.RequestException as exc:
        return CheckResult(False, f"Voice lookup failed: {exc}")


def check_persona_index(user_id: str) -> CheckResult:
    index_dir = Path('data/indexes') / user_id
    if not index_dir.exists():
        return CheckResult(False, f"Index directory missing: {index_dir}")
    files = list(index_dir.iterdir())
    if not files:
        return CheckResult(False, f"Index directory is empty: {index_dir}")
    return CheckResult(True, f"Persona index present with {len(files)} file(s).", {'files': [p.name for p in files]})


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description='Smoke-test the Voice Agent API stack.')
    parser.add_argument('--api-url', default=DEFAULT_API_URL, help='Base URL for the main API.')
    parser.add_argument('--trainer-url', default=DEFAULT_TRAINER_URL, help='Base URL for the trainer service.')
    parser.add_argument('--user-id', default='default', help='User ID to probe for voice/index assets.')
    parser.add_argument('--room-name', default='smoke-test', help='Room name (used as display name for token test).')
    args = parser.parse_args(argv)

    print('🧪 Voice Agent Smoke Tests')
    print('-------------------------')

    api_health = check_api_health(args.api_url)
    print(f"[API] {'OK' if api_health.ok else 'FAIL'} - {api_health.detail}")

    token_result = check_token(args.api_url, args.user_id, args.room_name)
    print(f"[API] {'OK' if token_result.ok else 'FAIL'} - {token_result.detail}")

    trainer_voice = check_trainer_voice(args.trainer_url, args.user_id)
    print(f"[Trainer] {'OK' if trainer_voice.ok else 'WARN'} - {trainer_voice.detail}")

    persona_index = check_persona_index(args.user_id)
    print(f"[Persona] {'OK' if persona_index.ok else 'WARN'} - {persona_index.detail}")

    print('\nSummary:')
    if api_health.ok and token_result.ok and trainer_voice.ok and persona_index.ok:
        print('✅ All components responded as expected.')
        if token_result.payload:
            print('  • LiveKit URL:', token_result.payload.get('url'))
        if trainer_voice.payload:
            print('  • Voice ID:', trainer_voice.payload.get('voice_id'))
    else:
        print('⚠ Some checks failed. Suggested follow-ups:')
        if not api_health.ok:
            print('  • Start API service: docker compose up api')
        if api_health.ok and not token_result.ok:
            print('  • Inspect API token logs; ensure credentials in .env are valid.')
        if not trainer_voice.ok:
            print('  • Run scripts/setup_voice.py to upload samples and create a voice.')
        if not persona_index.ok:
            print('  • Run scripts/setup_persona.py --reindex to build the index.')

    return 0 if (api_health.ok and token_result.ok) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
