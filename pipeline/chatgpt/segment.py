"""Stage 1: LLM-first segmentation + idea detection over ALL conversations.

For each conversation, render the canonical branch as an indexed transcript and
ask Haiku to split it into topic-coherent idea-segments, scoring each for
originality and crediting the spark (user / assistant / both). No regex gate —
the model finds the ideas.

Resumable + parallel: writes one JSONL line per conversation to segments.jsonl;
re-runs skip conv_ids already present. Idempotent.

Usage:
  python segment.py                 # full run (all conversations)
  python segment.py --limit 30      # test run on 30 conversations
  python segment.py --workers 12    # concurrency (default 10)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import anthropic

import db as dbm
from config import (
    DATA, MODEL_SEGMENT, SEGMENT_MIN_CHARS, SEGMENT_KEEP_SCORE, RENDER_CHAR_CAP,
)

SYSTEM = (Path(__file__).parent / "prompts" / "segment_system.txt").read_text()
OUT = DATA / "segments.jsonl"

SCHEMA = {
    "type": "object",
    "properties": {
        "segments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "msg_start": {"type": "integer"},
                    "msg_end": {"type": "integer"},
                    "topic_label": {"type": "string"},
                    "one_line_idea": {"type": "string"},
                    "is_original": {"type": "integer"},
                    "spark_by": {"type": "string", "enum": ["user", "assistant", "both"]},
                    "domain": {"type": "string"},
                },
                "required": [
                    "msg_start", "msg_end", "topic_label", "one_line_idea",
                    "is_original", "spark_by", "domain",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["segments"],
    "additionalProperties": False,
}


def seg_id(conv_id: str, s: int, e: int) -> str:
    return hashlib.sha1(f"{conv_id}:{s}:{e}".encode()).hexdigest()[:12]


def done_ids() -> set[str]:
    if not OUT.exists():
        return set()
    ids = set()
    for line in OUT.read_text().splitlines():
        if line.strip():
            ids.add(json.loads(line)["conv_id"])
    return ids


def segment_one(client, con, conv_id: str) -> dict | None:
    conv = dbm.load_conversation(con, conv_id)
    total_chars = sum(len(m.text) for m in conv.messages)
    if total_chars < SEGMENT_MIN_CHARS or not conv.messages:
        return {"conv_id": conv_id, "n_msgs": len(conv.messages), "segments": []}

    transcript, msgs = dbm.enumerate_transcript(conv, RENDER_CHAR_CAP)
    resp = client.messages.create(
        model=MODEL_SEGMENT,
        max_tokens=4000,
        system=SYSTEM,
        messages=[{"role": "user", "content": transcript}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    )
    text = next(b.text for b in resp.content if b.type == "text")
    segs = json.loads(text)["segments"]

    kept = []
    n = len(msgs)
    for s in segs:
        if s["is_original"] < SEGMENT_KEEP_SCORE:
            continue
        a = max(0, min(s["msg_start"], n - 1))
        b = max(a, min(s["msg_end"], n - 1))
        kept.append({
            "segment_id": seg_id(conv_id, a, b),
            "msg_start": a, "msg_end": b,
            "msg_id_start": msgs[a].id, "msg_id_end": msgs[b].id,
            "topic_label": s["topic_label"],
            "one_line_idea": s["one_line_idea"],
            "is_original": s["is_original"],
            "spark_by": s["spark_by"],
            "domain": s["domain"],
        })
    return {
        "conv_id": conv_id,
        "title": conv.title,
        "date": conv.create_time,
        "n_msgs": len(conv.messages),
        "segments": kept,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    client = anthropic.Anthropic()
    con = dbm.connect()

    already = done_ids()
    all_ids = [c for c in dbm.iter_conversation_ids(con) if c not in already]
    if args.limit:
        all_ids = all_ids[: args.limit]
    print(f"[segment] {len(already)} done, {len(all_ids)} to process (workers={args.workers})")

    # Each worker needs its own read-only connection (sqlite conns aren't threadsafe).
    def work(conv_id: str):
        c = dbm.connect()
        try:
            return segment_one(client, c, conv_id)
        finally:
            c.close()

    kept_segs = 0
    with OUT.open("a", encoding="utf-8") as fout, ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(work, cid): cid for cid in all_ids}
        for i, fut in enumerate(as_completed(futs), 1):
            cid = futs[fut]
            try:
                rec = fut.result()
            except Exception as e:
                print(f"  ! {cid[:8]} failed: {e}", file=sys.stderr)
                continue
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fout.flush()
            kept_segs += len(rec["segments"])
            if i % 25 == 0 or i == len(all_ids):
                print(f"[segment] {i}/{len(all_ids)} convs · {kept_segs} idea-segments kept")

    con.close()
    print(f"[segment] done. total idea-segments this run: {kept_segs} -> {OUT}")


if __name__ == "__main__":
    main()
