"""Voice (TTS) and lip-sync helper functions.

These are thin wrappers around external APIs. They assume you have
ELEVENLABS_API_KEY and D_ID_API_KEY environment variables configured.
"""

from __future__ import annotations

import base64
import os
from typing import Dict

import requests

# --- ElevenLabs TTS ---------------------------------------------------

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
EL_TTS_ENDPOINT = "https://api.elevenlabs.io/v1/text-to-speech"


def tts(text: str, voice_id: str = "Rachel") -> Dict[str, str]:
    if not ELEVENLABS_API_KEY:
        return {"error": "ELEVENLABS_API_KEY not set"}
    url = f"{EL_TTS_ENDPOINT}/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.3, "similarity_boost": 0.7},
    }
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code != 200:
        return {"error": f"TTS failed ({r.status_code})", "details": r.text}
    audio_b64 = base64.b64encode(r.content).decode()
    return {"audio_base64": audio_b64}


# --- D-ID Lip-sync -----------------------------------------------------

DID_API_KEY = os.getenv("D_ID_API_KEY")
DID_ENDPOINT = "https://api.d-id.com/talks"


def lip_sync(audio_b64: str, image_url: str) -> Dict[str, str]:
    if not DID_API_KEY:
        return {"error": "D_ID_API_KEY not set"}
    headers = {"Authorization": f"Basic {DID_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "script": {"type": "audio", "audio": audio_b64},
        "source_url": image_url,
        "driver_url": "bank://lively"
    }
    r = requests.post(DID_ENDPOINT, json=payload, headers=headers)
    if r.status_code != 201:
        return {"error": f"Lip-sync failed ({r.status_code})", "details": r.text}
    resp = r.json()
    return {"video_url": resp.get("result_url", "")}
