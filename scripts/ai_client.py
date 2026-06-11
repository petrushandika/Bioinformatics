"""
ai_client.py
Wrapper AI provider: Groq (utama) → Mistral (fallback).
"""

import os
import urllib.request
import json


def _post_json(url: str, headers: dict, body: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def _call_groq(prompt: str, system: str) -> str:
    result = _post_json(
        "https://api.groq.com/openai/v1/chat/completions",
        {"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
         "Content-Type": "application/json"},
        {"model": "llama3-70b-8192",
         "messages": [{"role": "system", "content": system},
                      {"role": "user",   "content": prompt}],
         "max_tokens": 4096, "temperature": 0.7},
    )
    return result["choices"][0]["message"]["content"]


def _call_mistral(prompt: str, system: str) -> str:
    result = _post_json(
        "https://api.mistral.ai/v1/chat/completions",
        {"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}",
         "Content-Type": "application/json"},
        {"model": "mistral-small-latest",
         "messages": [{"role": "system", "content": system},
                      {"role": "user",   "content": prompt}],
         "max_tokens": 4096},
    )
    return result["choices"][0]["message"]["content"]


PROVIDERS = [
    ("GROQ_API_KEY",    _call_groq,    "Groq (llama3-70b)"),
    ("MISTRAL_API_KEY", _call_mistral, "Mistral (mistral-small)"),
]


def generate(prompt: str, system: str = "You are a helpful assistant.") -> tuple[str, str]:
    """Coba Groq dulu, fallback ke Mistral. Return (teks, nama_provider)."""
    for env_var, fn, name in PROVIDERS:
        if os.environ.get(env_var):
            print(f"  AI provider: {name}")
            return fn(prompt, system), name

    raise RuntimeError(
        "Tidak ada API key ditemukan!\n"
        "Set di GitHub Secrets:\n"
        "  GROQ_API_KEY    → https://console.groq.com   (GRATIS)\n"
        "  MISTRAL_API_KEY → https://console.mistral.ai (GRATIS)"
    )
