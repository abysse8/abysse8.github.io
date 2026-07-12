"""Claude Code transcripts -> normalized JSONL.

Layout: ~/.claude/projects/<slug>/<sessionId>.jsonl (one line per event).
Keep type == user|assistant with a real message; skip isMeta, isSidechain, and
slash-command / system-reminder wrappers. message.content is a str or a blocks
array (keep type:"text" blocks; drop tool_use / tool_result).
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

PROJECTS = Path.home() / ".claude" / "projects"


def _text_from_message(message: dict) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(p for p in parts if p)


def parse_file(path: Path) -> Conversation | None:
    messages: list[Message] = []
    session_id = path.stem
    first_ts = None
    cwd = None

    for rec in iter_jsonl(path):
        rtype = rec.get("type")
        if rtype not in ("user", "assistant"):
            continue
        if rec.get("isMeta") or rec.get("isSidechain"):
            continue
        message = rec.get("message", {})
        role = normalize_role(message.get("role", rtype))
        if role is None:
            continue
        text = clean_text(_text_from_message(message))
        if role == "user" and is_noise_user_message(text):
            continue
        if not text:
            continue
        ts = rec.get("timestamp")
        if first_ts is None:
            first_ts = ts
        cwd = cwd or rec.get("cwd")
        messages.append(Message(role=role, ts=ts, text=text))

    if not messages:
        return None

    # Title from the first substantive user line.
    first_user = next((m.text for m in messages if m.role == "user"), "Claude Code session")
    title = first_user.split("\n", 1)[0][:70]

    return Conversation(
        source="claude_code",
        conversation_id=session_id,
        title=title,
        date=first_ts,
        messages=messages,
        cwd=cwd,
    )


def main(root: Path = PROJECTS) -> None:
    files = sorted(root.glob("**/*.jsonl"))
    convs = []
    for fp in files:
        try:
            c = parse_file(fp)
            if c:
                convs.append(c)
        except Exception as e:
            print(f"  ! skipped {fp.name}: {e}", file=sys.stderr)
    print(f"[claude_code] parsed {len(files)} files -> {len(convs)} usable conversations")
    write_jsonl("claude_code", convs)


if __name__ == "__main__":
    main()
