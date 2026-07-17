"""Token-free queue builder — no LLM calls.

The idea inventory (pipeline/data/raw/idea_inventory.json) is ALREADY scored by a
prior model run. This turns those scores into a review queue in the exact format
emit_drafts.py consumes (candidates.scored.json + review.md), applying only
deterministic, free filters:

  1. score threshold      — keep only high-rated ideas (default s >= 9)
  2. yours only           — attribution 'user' or 'both', never 'assistant'
  3. denylist HARD block  — pipeline/data/denylist.txt: any match on text/topic
                            is refused, logged, and never queued (protects people)
  4. dedupe vs published  — skip ideas already live in src/content/ideas/

Every queued item lands as `approve: no` in review.md. Nothing publishes until a
human flips it to `yes` and runs emit_drafts.py — which re-checks the denylist.

Run:  python pipeline/queue/build_queue.py [--min-score N]
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
from schema import ROOT, DATA, CURATED  # noqa: E402

INVENTORY = DATA / "raw" / "idea_inventory.json"
DENYLIST = DATA / "denylist.txt"
PUBLISHED = ROOT / "src" / "content" / "ideas"

# score -> maturity label for the fragment
STATUS = {7: "spark", 8: "growing", 9: "mature", 10: "mature"}


def load_denylist() -> list[str]:
    if not DENYLIST.exists():
        sys.exit(
            f"No denylist at {DENYLIST}. Copy pipeline/queue/denylist.example.txt "
            "there and fill it in first — refusing to run without the name block."
        )
    terms = []
    for line in DENYLIST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            terms.append(line.lower())
    return terms


def denied(text: str, terms: list[str]) -> str | None:
    low = text.lower()
    for t in terms:
        if t in low:
            return t
    return None


def published_keys() -> set[str]:
    """Normalized title-token signatures of already-live fragments, to dedupe."""
    keys = set()
    for md in PUBLISHED.glob("*.md"):
        m = re.search(r'title:\s*"?(.+?)"?\s*$', md.read_text(encoding="utf-8"), re.M)
        if m:
            keys.add(_sig(m.group(1)))
    return keys


def _sig(title: str) -> str:
    toks = re.sub(r"[^a-z0-9 ]", "", title.lower()).split()
    return " ".join(sorted(toks))


def frag_id(e: dict) -> str:
    return hashlib.sha1(f"{e['dt']}|{e['topic']}|{e['i'][:80]}".encode()).hexdigest()[:12]


def main() -> None:
    min_score = 9
    if "--min-score" in sys.argv:
        min_score = int(sys.argv[sys.argv.index("--min-score") + 1])

    ideas = json.loads(INVENTORY.read_text(encoding="utf-8"))
    terms = load_denylist()
    live = published_keys()

    scored: list[dict] = []
    counts = {"low_score": 0, "assistant": 0, "blocked": 0, "dup": 0, "queued": 0}
    blocked_log: list[tuple[str, str]] = []

    for e in ideas:
        if e["s"] < min_score:
            counts["low_score"] += 1
            continue
        if e["k"] == "assistant":
            counts["assistant"] += 1
            continue
        hit = denied(e["i"] + " " + e["topic"], terms)
        if hit:
            counts["blocked"] += 1
            blocked_log.append((e["dt"], hit))
            continue
        if _sig(e["topic"]) in live:
            counts["dup"] += 1
            continue

        counts["queued"] += 1
        scored.append({
            "fragment_id": frag_id(e),
            "title": e["topic"][:80],
            "date": e["dt"],
            "tags": [e["d"]][:4] or ["idea"],
            "status": STATUS.get(e["s"], "growing"),
            "distillation": e["i"],
            "attribution": "co-developed with ChatGPT" if e["k"] == "both"
                           else "my own idea, from a ChatGPT conversation",
            "sources": [],           # inventory keeps no verbatim quote — none invented
            "privacy_flags": [],     # denylist is the deterministic gate instead
            "_score": e["s"],
            "_domain": e["d"],
        })

    CURATED.mkdir(parents=True, exist_ok=True)
    (CURATED / "candidates.scored.json").write_text(
        json.dumps(scored, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Human-readable review queue. Flip `approve: no` -> `yes` to publish.
    scored.sort(key=lambda f: (-f["_score"], f["date"]))
    md = [
        "# Idea review queue",
        "",
        f"{len(scored)} candidates · score >= {min_score} · yours only · "
        f"{counts['blocked']} blocked by denylist · {counts['dup']} already live.",
        "",
        "Flip `approve: no` -> `approve: yes` for the ones to publish, then run:",
        "`python pipeline/emit_drafts.py`",
        "",
    ]
    for f in scored:
        md += [
            f"## {f['title']}",
            f"- fragment_id: `{f['fragment_id']}`",
            f"- date: {f['date']} · score: {f['_score']}/10 · domain: {f['_domain']} · {f['status']}",
            f"- approve: no",
            "",
            f"{f['distillation']}",
            "",
            "---",
            "",
        ]
    (CURATED / "review.md").write_text("\n".join(md), encoding="utf-8")

    print(f"[queue] {counts['queued']} queued  (threshold s>={min_score})")
    print(f"[queue] filtered: {counts['low_score']} low-score, "
          f"{counts['assistant']} assistant-only, {counts['dup']} already live")
    print(f"[queue] BLOCKED by denylist: {counts['blocked']}")
    for dt, term in blocked_log:
        print(f"          {dt}  matched '{term}'")
    print(f"[queue] wrote {CURATED/'review.md'} and candidates.scored.json")
    print("[queue] nothing publishes until you approve in review.md and run emit_drafts.py")


if __name__ == "__main__":
    main()
