"""ChatGPT data export -> normalized JSONL.

Drop the export zip (or its conversations.json) into pipeline/data/raw/.
Each conversation has: title, create_time (epoch), current_node, and mapping
(node-id -> {message, parent, children}). We walk parent pointers backward from
current_node to recover the canonical branch (survives edits/regenerations),
then reverse. Keep author.role in {user, assistant}, text content only.
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
    epoch_to_iso,
    is_noise_user_message,
    normalize_role,
    write_jsonl,
    RAW,
)


def _load_conversations() -> list[dict]:
    """Prefer an extracted conversations.json; else read it from any export zip."""
    direct = RAW / "conversations.json"
    if direct.exists():
        return json.loads(direct.read_text(encoding="utf-8"))
    for zp in sorted(RAW.glob("*.zip")):
        with zipfile.ZipFile(zp) as z:
            names = [n for n in z.namelist() if n.endswith("conversations.json")]
            # ChatGPT exports use "conversations.json"; claude.ai too — disambiguate
            # by structure (ChatGPT entries have a "mapping" key).
            for n in names:
                data = json.loads(z.read(n))
                if data and isinstance(data, list) and "mapping" in (data[0] or {}):
                    print(f"[chatgpt] reading {n} from {zp.name}")
                    return data
    return []


def _message_text(msg: dict) -> str:
    content = msg.get("content") or {}
    if content.get("content_type") != "text":
        return ""  # skip code/image/tool parts
    parts = content.get("parts") or []
    return "\n".join(p for p in parts if isinstance(p, str))


def _canonical_branch(mapping: dict, current_node: str | None) -> list[dict]:
    """Walk parent pointers from current_node to root, then reverse."""
    chain = []
    node_id = current_node
    # If no current_node, fall back to the node whose parent is None.
    if not node_id:
        node_id = next((nid for nid, n in mapping.items() if not n.get("parent")), None)
        # then follow first children down
        out = []
        while node_id:
            node = mapping.get(node_id, {})
            if node.get("message"):
                out.append(node["message"])
            children = node.get("children") or []
            node_id = children[0] if children else None
        return out
    while node_id:
        node = mapping.get(node_id)
        if not node:
            break
        if node.get("message"):
            chain.append(node["message"])
        node_id = node.get("parent")
    chain.reverse()
    return chain


def parse_conversation(conv: dict) -> Conversation | None:
    mapping = conv.get("mapping") or {}
    branch = _canonical_branch(mapping, conv.get("current_node"))
    conv_ct = conv.get("create_time")
    messages: list[Message] = []
    for msg in branch:
        author = (msg.get("author") or {}).get("role", "")
        role = normalize_role(author)
        if role is None:
            continue
        text = clean_text(_message_text(msg))
        if role == "user" and is_noise_user_message(text):
            continue
        if not text:
            continue
        ts = epoch_to_iso(msg.get("create_time") or conv_ct)
        messages.append(Message(role=role, ts=ts, text=text))

    if not messages:
        return None

    return Conversation(
        source="chatgpt",
        conversation_id=conv.get("conversation_id") or conv.get("id") or conv.get("title", "chatgpt"),
        title=(conv.get("title") or "ChatGPT conversation")[:80],
        date=epoch_to_iso(conv_ct) or messages[0].ts,
        messages=messages,
    )


def main() -> None:
    raw = _load_conversations()
    if not raw:
        print("[chatgpt] no export found in pipeline/data/raw/ (skipping)")
        return
    convs = []
    for c in raw:
        try:
            parsed = parse_conversation(c)
            if parsed:
                convs.append(parsed)
        except Exception as e:
            print(f"  ! skipped a conversation: {e}", file=sys.stderr)
    print(f"[chatgpt] parsed {len(raw)} conversations -> {len(convs)} usable")
    write_jsonl("chatgpt", convs)


if __name__ == "__main__":
    main()
