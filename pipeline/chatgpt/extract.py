"""Stage 3: deep extraction of each shortlisted idea-segment (Opus 4.8).

Pulls the segment's real messages from the DB and articulates the idea as a
spark -> crystallization pair with honest attribution. Structured output.

Resumable: appends to fragments.jsonl, skips segment_ids already done.
Usage: python extract.py [--limit N] [--workers 6]
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import anthropic

import db as dbm
from config import DATA, MODEL_EXTRACT, EXTRACT_EFFORT

SYSTEM = (Path(__file__).parent / "prompts" / "extract_system.txt").read_text()
OUT = DATA / "fragments.jsonl"

_QUOTE = {
    "type": "object",
    "properties": {
        "speaker": {"type": "string", "enum": ["you", "chatgpt"]},
        "quote": {"type": "string"},
    },
    "required": ["speaker", "quote"],
    "additionalProperties": False,
}
SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "distillation": {"type": "string"},
        "spark": _QUOTE,
        "crystallization": _QUOTE,
        "attribution": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "status": {"type": "string", "enum": ["spark", "growing", "mature"]},
        "unresolved": {"type": "string"},
        "privacy_flags": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "title", "distillation", "spark", "crystallization", "attribution",
        "tags", "status", "unresolved", "privacy_flags",
    ],
    "additionalProperties": False,
}


def done_ids() -> set[str]:
    if not OUT.exists():
        return set()
    return {json.loads(l)["segment_id"] for l in OUT.read_text().splitlines() if l.strip()}


def render_segment(con, conv_id: str, a: int, b: int) -> str:
    conv = dbm.load_conversation(con, conv_id)
    msgs = conv.messages[a : b + 1]
    return "\n\n".join(f"[{a + i}] {m.role}: {m.text}" for i, m in enumerate(msgs))


def extract_one(client, con, seg: dict) -> dict | None:
    transcript = render_segment(con, seg["conv_id"], seg["msg_start"], seg["msg_end"])
    if not transcript.strip():
        return None
    resp = client.messages.create(
        model=MODEL_EXTRACT,
        max_tokens=4000,
        system=SYSTEM,
        messages=[{"role": "user", "content": transcript}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}, "effort": EXTRACT_EFFORT},
    )
    text = next(b.text for b in resp.content if b.type == "text")
    frag = json.loads(text)
    frag["segment_id"] = seg["segment_id"]
    frag["conv_id"] = seg["conv_id"]
    frag["date"] = seg.get("date")
    frag["domain"] = seg.get("domain")
    frag["is_original"] = seg.get("is_original")
    return frag


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    shortlist = json.loads((DATA / "shortlist.json").read_text())
    already = done_ids()
    todo = [s for s in shortlist if s["segment_id"] not in already]
    if args.limit:
        todo = todo[: args.limit]
    print(f"[extract] {len(already)} done, {len(todo)} to extract (workers={args.workers})")

    client = anthropic.Anthropic()

    def work(seg):
        c = dbm.connect()
        try:
            return extract_one(client, c, seg)
        finally:
            c.close()

    n = 0
    with OUT.open("a", encoding="utf-8") as fout, ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(work, s): s for s in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            s = futs[fut]
            try:
                frag = fut.result()
            except Exception as e:
                print(f"  ! {s['segment_id']} failed: {e}", file=sys.stderr)
                continue
            if frag:
                fout.write(json.dumps(frag, ensure_ascii=False) + "\n")
                fout.flush()
                n += 1
            if i % 10 == 0 or i == len(todo):
                print(f"[extract] {i}/{len(todo)}")
    print(f"[extract] wrote {n} fragments -> {OUT}")


if __name__ == "__main__":
    main()
