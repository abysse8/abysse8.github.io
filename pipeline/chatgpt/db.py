"""Read-only access to the ChatGPT memory DB + canonical-branch rendering.

Never opens the DB for writing. The canonical branch is the thread the owner
actually saw: walk `conversations.current_node` up via `messages.parent_id` to
the root, then reverse. That resolves the "dirty conversation" mapping tree to
the single linear transcript we segment and quote from.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from config import db_path, RENDER_CHAR_CAP


@dataclass
class Msg:
    id: str
    role: str            # "user" | "assistant"
    text: str
    content_type: str
    create_time: float | None


@dataclass
class Conversation:
    id: str
    title: str
    create_time: float | None
    update_time: float | None
    model: str | None
    messages: list[Msg] = field(default_factory=list)


def connect(path: Path | None = None) -> sqlite3.Connection:
    p = path or db_path()
    con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def _text_of(row: sqlite3.Row) -> str:
    """content_text is populated by the importer; fall back to raw_json parts."""
    t = row["content_text"]
    if t:
        return t
    try:
        raw = json.loads(row["raw_json"] or "{}")
        parts = (raw.get("content") or {}).get("parts") or []
        return "\n\n".join(p for p in parts if isinstance(p, str))
    except Exception:
        return ""


def canonical_branch(con: sqlite3.Connection, conv_id: str, current_node: str) -> list[Msg]:
    """Walk current_node -> root via parent_id; return root->leaf message order.
    Skips nodes with no usable text (system/root placeholders, empty turns)."""
    rows = {
        r["id"]: r
        for r in con.execute(
            "SELECT id,parent_id,author_role,content_type,content_text,raw_json,create_time "
            "FROM messages WHERE conversation_id=?",
            (conv_id,),
        )
    }
    chain: list[Msg] = []
    node = current_node
    seen = set()
    while node and node in rows and node not in seen:
        seen.add(node)
        r = rows[node]
        role = r["author_role"]
        text = _text_of(r).strip()
        if role in ("user", "assistant") and text:
            chain.append(
                Msg(id=r["id"], role=role, text=text, content_type=r["content_type"] or "text",
                    create_time=r["create_time"])
            )
        node = r["parent_id"]
    chain.reverse()
    return chain


def load_conversation(con: sqlite3.Connection, conv_id: str) -> Conversation:
    c = con.execute(
        "SELECT id,title,current_node,create_time,update_time,default_model_slug "
        "FROM conversations WHERE id=?",
        (conv_id,),
    ).fetchone()
    msgs = canonical_branch(con, conv_id, c["current_node"] or "")
    return Conversation(
        id=c["id"], title=c["title"] or "", create_time=c["create_time"],
        update_time=c["update_time"], model=c["default_model_slug"], messages=msgs,
    )


def iter_conversation_ids(con: sqlite3.Connection):
    for r in con.execute("SELECT id FROM conversations ORDER BY create_time"):
        yield r["id"]


def enumerate_transcript(conv: Conversation, char_cap: int = RENDER_CHAR_CAP) -> tuple[str, list[Msg]]:
    """Render the canonical branch as an indexed transcript the LLM can cite by
    index: `[0] user: …`. Returns (text, messages) where messages[i] is index i.
    If the thread exceeds char_cap, the middle is elided (head + tail kept) but
    indices still map 1:1 to the returned message list."""
    msgs = conv.messages
    lines, used = [], 0
    for i, m in enumerate(msgs):
        block = f"[{i}] {m.role}: {m.text}"
        lines.append(block)
        used += len(block)
    text = "\n\n".join(lines)
    if len(text) <= char_cap:
        return text, msgs

    # Over cap: keep head and tail, note the elision. Indices preserved.
    head, tail, half = [], [], char_cap // 2
    u = 0
    for i, m in enumerate(msgs):
        block = f"[{i}] {m.role}: {m.text}"
        if u + len(block) > half:
            break
        head.append(block)
        u += len(block)
    u = 0
    for j in range(len(msgs) - 1, -1, -1):
        m = msgs[j]
        block = f"[{j}] {m.role}: {m.text}"
        if u + len(block) > half:
            break
        tail.append(block)
        u += len(block)
    tail.reverse()
    text = "\n\n".join(head) + "\n\n[… middle elided for length …]\n\n" + "\n\n".join(tail)
    return text, msgs


if __name__ == "__main__":
    # Smoke test: render the Wavelet Theory thread.
    con = connect()
    cid = con.execute(
        "SELECT id FROM conversations WHERE title LIKE '%Wavelet Theory%' LIMIT 1"
    ).fetchone()
    if cid:
        conv = load_conversation(con, cid["id"])
        txt, msgs = enumerate_transcript(conv)
        print(f"conv {conv.id} '{conv.title}' — {len(msgs)} msgs, {len(txt)} chars")
        print(txt[:600])
    con.close()
