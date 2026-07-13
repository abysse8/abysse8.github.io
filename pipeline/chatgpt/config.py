"""Shared config for the ChatGPT idea-mining funnel.

The DB is the owner's memory store — we only ever open it read-only.
Default path is a local gitignored cache (fast); falls back to the canonical
Windows copy. Override with the CHATGPT_DB env var.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # repo root

# Load a gitignored pipeline/.env (KEY=VALUE lines) into the environment so the
# SDK picks up ANTHROPIC_API_KEY without polluting shell profiles. Existing env
# vars win.
_ENV = ROOT / "pipeline" / ".env"
if _ENV.exists():
    for _line in _ENV.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        os.environ.setdefault(_k.strip(), _v.strip())
DATA = ROOT / "pipeline" / "data" / "chatgpt"        # gitignored
CURATED = ROOT / "pipeline" / "data" / "curated"     # gitignored (emit gate reads here)

_LOCAL_DB = DATA / "memory.sqlite"
_CANONICAL_DB = Path("/mnt/c/Users/J3/Documents/SVT/Personal/chatgpt-memory-db/memory.sqlite")


def db_path() -> Path:
    env = os.environ.get("CHATGPT_DB")
    if env:
        return Path(env)
    if _LOCAL_DB.exists():
        return _LOCAL_DB
    return _CANONICAL_DB


# Models — segment/rank are cheap batch work; extract/cluster need nuance.
MODEL_SEGMENT = "claude-haiku-4-5"
MODEL_EXTRACT = "claude-opus-4-8"
MODEL_CLUSTER = "claude-opus-4-8"

# Funnel knobs
SEGMENT_MIN_CHARS = 200        # skip near-empty conversations (trivial, non-semantic)
SEGMENT_KEEP_SCORE = 4         # drop idea-segments scoring below this in stage 1
RENDER_CHAR_CAP = 30_000       # cap per-conversation transcript fed to the LLM
SHORTLIST_SIZE = 250           # segments passed to deep extraction
EXTRACT_EFFORT = "low"         # Opus effort for extraction; "low" keeps cost bounded
