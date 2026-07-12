"""claude.ai data export -> normalized JSONL.

Drop the export zip (or conversations.json) into pipeline/data/raw/.
Flat structure: each conversation has uuid, name, created_at, and chat_messages[]
with sender (human/assistant), created_at, and text (newer exports also carry a
content[] blocks array — prefer text, fall back to joining content[].text).
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

from schema import (
    Conversation,
    Message,
    clean_text,
    is_noise_user_message,
    normalize_role,
    write_jsonl,
    RAW,
)


def _load_conversations() -> list[dict]:
    # A claude.ai export may sit beside a ChatGPT one; disambiguate by structure
    # (claude.ai entries have "chat_messages", not "mapping").
    direct = RAW / "claude_conversations.json"
    if direct.exists():
        return json.loads(direct.read_text(encoding="utf-8"))
    for zp in sorted(RAW.glob("*.zip")):
        with zipfile.ZipFile(zp) as z:
            for n in z.namelist():
                if not n.endswith("conversations.json"):
                    continue
                data = json.loads(z.read(n))
                if data and isinstance(data, list) and "chat_messages" in (data[0] or {}):
                    print(f"[claude_ai] reading {n} from {zp.name}")
                    return data
    return []


def _message_text(msg: dict) -> str:
    if msg.get("text"):
        return msg["text"]
    parts = []
    for block in msg.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(p for p in parts if p)


def parse_conversation(conv: dict) -> Conversation | None:
    messages: list[Message] = []
    for msg in conv.get("chat_messages") or []:
        role = normalize_role(msg.get("sender", ""))
        if role is None:
            continue
        text = clean_text(_message_text(msg))
        if role == "user" and is_noise_user_message(text):
            continue
        if not text:
            continue
        messages.append(Message(role=role, ts=msg.get("created_at"), text=text))

    if not messages:
        return None

    return Conversation(
        source="claude_ai",
        conversation_id=conv.get("uuid", conv.get("name", "claude")),
        title=(conv.get("name") or "Claude conversation")[:80],
        date=conv.get("created_at") or messages[0].ts,
        messages=messages,
    )


def main() -> None:
    raw = _load_conversations()
    if not raw:
        print("[claude_ai] no export found in pipeline/data/raw/ (skipping)")
        return
    convs = []
    for c in raw:
        try:
            parsed = parse_conversation(c)
            if parsed:
                convs.append(parsed)
        except Exception as e:
            print(f"  ! skipped a conversation: {e}", file=sys.stderr)
    print(f"[claude_ai] parsed {len(raw)} conversations -> {len(convs)} usable")
    write_jsonl("claude_ai", convs)


if __name__ == "__main__":
    main()
