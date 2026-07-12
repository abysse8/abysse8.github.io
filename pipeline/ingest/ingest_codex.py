"""Codex CLI rollouts -> normalized JSONL.

Layout: ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl
  line 1: {"type":"session_meta","payload":{id, timestamp, cwd, ...}}
  then:   {"type":"response_item","payload":{"type":"message","role","content":[...]}}

Keep only role user/assistant messages; extract input_text/output_text items.
Drop function_call*, reasoning, event_msg, turn_context, and the developer role.
Drop user messages that are AGENTS.md / env-context / permissions injections.
"""

from __future__ import annotations

import sys
from pathlib import Path

from schema import (
    Conversation,
    Message,
    clean_text,
    is_noise_user_message,
    normalize_role,
    write_jsonl,
    iter_jsonl,
)

SESSIONS = Path.home() / ".codex" / "sessions"


def _text_from_content(content) -> str:
    parts = []
    for item in content or []:
        if isinstance(item, dict) and item.get("type") in ("input_text", "output_text"):
            parts.append(item.get("text", ""))
    return "\n".join(p for p in parts if p)


def parse_file(path: Path) -> Conversation | None:
    meta = None
    messages: list[Message] = []
    for rec in iter_jsonl(path):
        if rec.get("type") == "session_meta":
            meta = rec.get("payload", {})
            continue
        if rec.get("type") != "response_item":
            continue
        payload = rec.get("payload", {})
        if payload.get("type") != "message":
            continue
        role = normalize_role(payload.get("role", ""))
        if role is None:
            continue
        text = clean_text(_text_from_content(payload.get("content")))
        if role == "user" and is_noise_user_message(text):
            continue
        if not text:
            continue
        messages.append(Message(role=role, ts=rec.get("timestamp"), text=text))

    if meta is None or not messages:
        return None

    return Conversation(
        source="codex",
        conversation_id=meta.get("id", path.stem),
        title=f"Codex session ({Path(meta.get('cwd', '')).name or 'session'})",
        date=meta.get("timestamp") or meta.get("payload", {}).get("timestamp"),
        messages=messages,
        cwd=meta.get("cwd"),
    )


def main(root: Path = SESSIONS) -> None:
    files = sorted(root.glob("**/rollout-*.jsonl"))
    convs = []
    for fp in files:
        try:
            c = parse_file(fp)
            if c:
                convs.append(c)
        except Exception as e:  # one bad file shouldn't sink the run
            print(f"  ! skipped {fp.name}: {e}", file=sys.stderr)
    print(f"[codex] parsed {len(files)} files -> {len(convs)} usable conversations")
    write_jsonl("codex", convs)


if __name__ == "__main__":
    main()
