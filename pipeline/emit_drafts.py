"""Human gate -> Astro content collection entries.

Reads pipeline/data/curated/review.md; for every fragment marked `approve: yes`,
writes src/content/ideas/<date>-<slug>.md with draft:true. Never overwrites an
existing file. Fragments with privacy flags need an explicit --allow-flagged ack.

Consumes the lineage fragments written by pipeline/chatgpt/cluster.py (spark +
crystallization sources, attribution, revisits).

Run after editing review.md:  python emit_drafts.py [--allow-flagged]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "ingest"))
from schema import ROOT, CURATED  # noqa: E402

IDEAS_DIR = ROOT / "src" / "content" / "ideas"


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60] or "fragment"


def parse_approvals(review: str) -> set[str]:
    approved = set()
    for block in re.split(r"^## ", review, flags=re.MULTILINE):
        fid = re.search(r"fragment_id:\s*`([^`]+)`", block)
        if fid and re.search(r"approve:\s*yes", block, re.IGNORECASE):
            approved.add(fid.group(1))
    return approved


def q(s) -> str:
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def source_entries(frag: dict) -> list[str]:
    """Emit the canonical source's spark + crystallization as two labelled entries."""
    src = (frag.get("sources") or [{}])[0]
    date = src.get("date") or frag.get("date")
    lines: list[str] = []
    for role in ("spark", "crystallization"):
        blk = src.get(role)
        if not blk or not blk.get("quote"):
            continue
        lines += [
            f"  - kind: {src.get('kind', 'chatgpt')}",
            f"    date: {date}",
            f"    speaker: {blk.get('speaker', 'you')}",
            f"    role: {role}",
            f"    quote: {q(blk['quote'])}",
        ]
    return lines


def main() -> None:
    allow_flagged = "--allow-flagged" in sys.argv
    review_path = CURATED / "review.md"
    scored_path = CURATED / "candidates.scored.json"
    if not review_path.exists() or not scored_path.exists():
        sys.exit("Run the pipeline first — review.md / candidates.scored.json missing.")

    approved = parse_approvals(review_path.read_text())
    if not approved:
        print("No fragments marked `approve: yes` — nothing to emit.")
        return

    scored = {f["fragment_id"]: f for f in json.loads(scored_path.read_text())}
    IDEAS_DIR.mkdir(parents=True, exist_ok=True)

    written = skipped = blocked = 0
    for fid in approved:
        f = scored.get(fid)
        if not f:
            print(f"  ? {fid} approved but not in scored data — skipping")
            continue
        if f.get("privacy_flags") and not allow_flagged:
            print(f"  ⚠️ {fid} has privacy flags {f['privacy_flags']} — re-run with --allow-flagged")
            blocked += 1
            continue

        date = (f.get("date") or "2025-01-01")[:10]
        out = IDEAS_DIR / f"{date}-{slugify(f['title'])}.md"
        if out.exists():
            print(f"  = {out.name} exists — not overwriting")
            skipped += 1
            continue

        tags = ", ".join(q(t) for t in f["tags"][:4])
        fm = [
            "---",
            f"title: {q(f['title'][:80])}",
            f"date: {date}",
            f"tags: [{tags}]",
            f"status: {f['status']}",
            "draft: true",
        ]
        if f.get("attribution"):
            fm.append(f"attribution: {q(f['attribution'])}")
        revisits = [d for d in (f.get("revisits") or []) if d and d != date]
        if revisits:
            fm.append("revisits: [" + ", ".join(revisits) + "]")
        fm.append("sources:")
        fm += source_entries(f)
        fm += ["---", "", f["distillation"], ""]
        out.write_text("\n".join(fm))
        print(f"  + {out.name}")
        written += 1

    print(f"\nWrote {written}, skipped {skipped} existing, blocked {blocked} flagged.")
    print("All drafts are draft:true — edit, then flip draft:false per file to publish.")


if __name__ == "__main__":
    main()
