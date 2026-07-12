"""Normalized schema every parser targets, plus shared text hygiene.

One JSONL record per conversation:
    {source, conversation_id, title, date, cwd?, messages: [{role, ts, text}]}

Roles are normalized to "user" | "assistant". All parsers strip agent/tool
plumbing and environment-context injections so downstream curation only ever
sees human-authored prose and model replies.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path

# Repo root = two levels up from this file (pipeline/ingest/schema.py).
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "pipeline" / "data"
NORMALIZED = DATA / "normalized"
RAW = DATA / "raw"
CURATED = DATA / "curated"

# XML-ish blocks that are harness/agent plumbing, not anything the human wrote.
# Matched anywhere in a message; if a user message is *only* these, it's dropped.
_NOISE_TAGS = (
    "environment_context",
    "user_instructions",
    "system-reminder",
    "command-name",
    "command-message",
    "command-args",
    "local-command-caveat",
    "local-command-stdout",
    "permissions instructions",
    "INSTRUCTIONS",
)
_NOISE_RE = re.compile(
    r"<(" + "|".join(re.escape(t) for t in _NOISE_TAGS) + r")>.*?</\1>",
    re.DOTALL | re.IGNORECASE,
)
# Some injections are self-closing-ish or unpaired; nuke obvious leaders too.
_LEADER_RE = re.compile(
    r"^\s*(#\s*AGENTS\.md|<permissions|<environment_context|<user_instructions)",
    re.IGNORECASE,
)


@dataclass
class Message:
    role: str  # "user" | "assistant"
    ts: str | None  # ISO8601 or None
    text: str


@dataclass
class Conversation:
    source: str  # "chatgpt" | "claude_ai" | "codex" | "claude_code"
    conversation_id: str
    title: str
    date: str | None  # ISO8601 of first message
    messages: list[Message] = field(default_factory=list)
    cwd: str | None = None

    def to_json(self) -> dict:
        d = asdict(self)
        return d


def clean_text(text: str) -> str:
    """Strip harness plumbing; return '' if nothing human remains."""
    if not text:
        return ""
    text = _NOISE_RE.sub(" ", text)
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def is_noise_user_message(text: str) -> bool:
    """True if a user message is really an env/context/agent injection."""
    if not text:
        return True
    if _LEADER_RE.match(text):
        return True
    # Heavy tag soup with little prose left after cleaning.
    return len(clean_text(text)) < 12


def epoch_to_iso(v) -> str | None:
    if v is None:
        return None
    try:
        return datetime.fromtimestamp(float(v), tz=timezone.utc).isoformat()
    except (ValueError, OSError, TypeError):
        return None


def normalize_role(role: str) -> str | None:
    r = (role or "").lower()
    if r in ("user", "human"):
        return "user"
    if r == "assistant":
        return "assistant"
    return None  # developer / system / tool -> dropped


def write_jsonl(source: str, conversations: list[Conversation]) -> Path:
    """Rebuild <source>.jsonl from scratch — raw data is the source of truth,
    so re-runs are deterministic and idempotent."""
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    out = NORMALIZED / f"{source}.jsonl"
    kept = [c for c in conversations if c.messages]
    with out.open("w", encoding="utf-8") as f:
        for conv in kept:
            f.write(json.dumps(conv.to_json(), ensure_ascii=False) + "\n")
    print(f"[{source}] wrote {len(kept)} conversations -> {out}")
    return out


def iter_jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)
