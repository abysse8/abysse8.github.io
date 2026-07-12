"""Human gate → Astro content collection entries.

Reads pipeline/data/curated/review.md, and for every fragment the human marked
`approve: yes`, writes src/content/ideas/<date>-<slug>.md with draft:true.
Never overwrites an existing file. Fragments with privacy flags require an
explicit `--allow-flagged` acknowledgement.

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
SOURCE_KIND = {"chatgpt": "chatgpt", "claude_ai": "claude", "codex": "codex", "claude_code": "claude-code"}


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60] or "fragment"


def parse_approvals(review: str) -> set[str]:
    """Return fragment_ids whose block contains `approve: yes`."""
    approved = set()
    blocks = re.split(r"^## ", review, flags=re.MULTILINE)
    for block in blocks:
        fid = re.search(r"fragment_id:\s*`([^`]+)`", block)
        if fid and re.search(r"approve:\s*yes", block, re.IGNORECASE):
            approved.add(fid.group(1))
    return approved


def yaml_escape(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> None:
    allow_flagged = "--allow-flagged" in sys.argv
    review_path = CURATED / "review.md"
    scored_path = CURATED / "candidates.scored.json"
    if not review_path.exists() or not scored_path.exists():
        sys.exit("Run llm_curate.py first — review.md / candidates.scored.json missing.")

    approved = parse_approvals(review_path.read_text())
    if not approved:
        print("No fragments marked `approve: yes` in review.md — nothing to emit.")
        return

    scored = {s["fragment_id"]: s for s in json.loads(scored_path.read_text())}
    IDEAS_DIR.mkdir(parents=True, exist_ok=True)

    written = skipped = blocked = 0
    for fid in approved:
        s = scored.get(fid)
        if not s:
            print(f"  ? {fid} approved but not in scored data — skipping")
            continue
        if s.get("privacy_flags") and not allow_flagged:
            print(f"  ⚠️ {fid} has privacy flags {s['privacy_flags']} — re-run with --allow-flagged to emit")
            blocked += 1
            continue

        date = (s.get("date") or "2025-01-01")[:10]
        fname = f"{date}-{slugify(s['title'])}.md"
        out = IDEAS_DIR / fname
        if out.exists():
            print(f"  = {fname} exists — not overwriting")
            skipped += 1
            continue

        kind = SOURCE_KIND.get(s.get("source", ""), "manual")
        tags = ", ".join(yaml_escape(t) for t in s["tags"][:4])
        fm = [
            "---",
            f"title: {yaml_escape(s['title'][:80])}",
            f"date: {date}",
            f"tags: [{tags}]",
            f"status: {s['status_guess']}",
            "draft: true",
            "sources:",
            f"  - kind: {kind}",
            f"    date: {date}",
            f"    fragment_id: {yaml_escape(fid)}",
            f"    quote: {yaml_escape(s['quote'])}",
            "---",
            "",
            s["distillation"],
            "",
        ]
        out.write_text("\n".join(fm))
        print(f"  + {fname}")
        written += 1

    print(f"\nWrote {written}, skipped {skipped} existing, blocked {blocked} flagged.")
    print("All drafts are draft:true — edit, then flip draft:false per file to publish.")


if __name__ == "__main__":
    main()
