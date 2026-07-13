"""Stage 2: flatten idea-segments and shortlist the top ones for deep extraction.

Reads segments.jsonl (Stage 1 output), takes every kept segment, ranks by
originality (tiebreak: recency), keeps the top SHORTLIST_SIZE. No LLM — the
segmentation scores already reflect an LLM judgment.

Usage: python rank.py [--size 250]
"""

from __future__ import annotations

import argparse
import json

from config import DATA, SHORTLIST_SIZE


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=SHORTLIST_SIZE)
    args = ap.parse_args()

    src = DATA / "segments.jsonl"
    if not src.exists():
        raise SystemExit("Run segment.py first — no segments.jsonl.")

    segs = []
    for line in src.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        for s in rec["segments"]:
            segs.append({
                **s,
                "conv_id": rec["conv_id"],
                "conv_title": rec.get("title", ""),
                "date": rec.get("date"),
            })

    segs.sort(key=lambda s: (s["is_original"], s.get("date") or 0), reverse=True)
    shortlist = segs[: args.size]

    out = DATA / "shortlist.json"
    out.write_text(json.dumps(shortlist, ensure_ascii=False, indent=2))
    hi = sum(1 for s in shortlist if s["is_original"] >= 8)
    print(f"[rank] {len(segs)} idea-segments total; shortlisted {len(shortlist)} "
          f"({hi} scored >=8). cut score = "
          f"{shortlist[-1]['is_original'] if shortlist else 'n/a'} -> {out}")


if __name__ == "__main__":
    main()
