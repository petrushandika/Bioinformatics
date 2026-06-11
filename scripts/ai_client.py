"""
ai_client.py
Wrapper untuk berbagai AI provider gratis.
Prioritas: Groq → Mistral → Gemini → Anthropic
Cukup set salah satu API key di GitHub Secrets.
"""

import os
import urllib.request
import urllib.error
import json


def _post_json(url: str, headers: dict, body: dict) -> str:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
    return result


# ── Provider implementations ──────────────────────────────────────────────────

def _call_groq(prompt: str, system: str) -> str:
    """Groq — gratis, model: llama3-70b / mixtral-8x7b"""
    key = os.environ["GROQ_API_KEY"]
    body = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 4096,
        "temperature": 0.7,
    }
    result = _post_json(
        "https://api.groq.com/openai/v1/chat/completions",
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        body,
    )
    return result["choices"][0]["message"]["content"]


def _call_mistral(prompt: str, system: str) -> str:
    """Mistral — gratis tier, model: mistral-small-latest"""
    key = os.environ["MISTRAL_API_KEY"]
    body = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 4096,
    }
    result = _post_json(
        "https://api.mistral.ai/v1/chat/completions",
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        body,
    )
    return result["choices"][0]["message"]["content"]


def _call_gemini(prompt: str, system: str) -> str:
    """Google Gemini — gratis tier, model: gemini-1.5-flash"""
    key = os.environ["GEMINI_API_KEY"]
    body = {
        "contents": [{"parts": [{"text": f"{system}\n\n{prompt}"}]}],
        "generationConfig": {"maxOutputTokens": 4096, "temperature": 0.7},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    result = _post_json(url, {"Content-Type": "application/json"}, body)
    return result["candidates"][0]["content"]["parts"][0]["text"]


def _call_anthropic(prompt: str, system: str) -> str:
    """Anthropic Claude — berbayar, sebagai fallback terakhir"""
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ── Public API ────────────────────────────────────────────────────────────────

PROVIDERS = [
    ("GROQ_API_KEY",      _call_groq,      "Groq (llama3-70b)"),
    ("MISTRAL_API_KEY",   _call_mistral,   "Mistral (mistral-small)"),
    ("GEMINI_API_KEY",    _call_gemini,    "Gemini (gemini-1.5-flash)"),
    ("ANTHROPIC_API_KEY", _call_anthropic, "Anthropic (claude-sonnet)"),
]


def generate(prompt: str, system: str = "You are a helpful assistant.") -> tuple[str, str]:
    """
    Coba provider satu per satu berdasarkan API key yang tersedia.
    Return (response_text, provider_name).
    Raise RuntimeError jika tidak ada key yang tersedia.
    """
    for env_var, fn, name in PROVIDERS:
        if os.environ.get(env_var):
            print(f"  Menggunakan AI provider: {name}")
            return fn(prompt, system), name

    raise RuntimeError(
        "Tidak ada AI API key yang ditemukan!\n"
        "Set salah satu di GitHub Secrets:\n"
        "  GROQ_API_KEY      → https://console.groq.com  (GRATIS)\n"
        "  MISTRAL_API_KEY   → https://console.mistral.ai (GRATIS)\n"
        "  GEMINI_API_KEY    → https://aistudio.google.com (GRATIS)\n"
        "  ANTHROPIC_API_KEY → https://console.anthropic.com (berbayar)"
    )
