"""Stage (b): LLM curation judge.

Reads candidates.json, scores each candidate with a cheap batch model, writes
candidates.scored.json + a human-readable review.md. Nothing is published here —
emit_drafts.py gates on human approval afterward.

Requires: pip install anthropic ; ANTHROPIC_API_KEY set (or `ant auth login`).
Model: claude-haiku-4-5 — cheap batch classification is exactly its lane.
Idempotent: skips fragment_ids already present in candidates.scored.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
from schema import CURATED  # noqa: E402

MODEL = "claude-haiku-4-5"
BATCH = 20
PROMPT = (Path(__file__).parent / "prompts" / "curator_system.txt").read_text()

VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fragment_id": {"type": "string"},
                    "verdict": {"type": "string", "enum": ["idea", "routine", "borderline"]},
                    "score": {"type": "integer"},
                    "title": {"type": "string"},
                    "distillation": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "status_guess": {"type": "string", "enum": ["spark", "growing", "mature"]},
                    "quote": {"type": "string"},
                    "privacy_flags": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "fragment_id", "verdict", "score", "title", "distillation",
                    "tags", "status_guess", "quote", "privacy_flags",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["results"],
    "additionalProperties": False,
}


def judge_batch(client, batch: list[dict]) -> list[dict]:
    payload = [
        {
            "fragment_id": c["fragment_id"],
            "user_message": c["user_text"],
            "assistant_context": c["assistant_context"][:800],
        }
        for c in batch
    ]
    resp = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        system=PROMPT,
        messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
        output_config={"format": {"type": "json_schema", "schema": VERDICT_SCHEMA}},
    )
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text)["results"]


def main() -> None:
    import anthropic

    cand_path = CURATED / "candidates.json"
    if not cand_path.exists():
        sys.exit("Run prefilter.py first — no candidates.json found.")
    candidates = json.loads(cand_path.read_text())
    by_id = {c["fragment_id"]: c for c in candidates}

    scored_path = CURATED / "candidates.scored.json"
    scored = json.loads(scored_path.read_text()) if scored_path.exists() else []
    done = {s["fragment_id"] for s in scored}
    todo = [c for c in candidates if c["fragment_id"] not in done]
    print(f"[curate] {len(done)} already scored, {len(todo)} to judge")

    client = anthropic.Anthropic()
    for i in range(0, len(todo), BATCH):
        batch = todo[i : i + BATCH]
        try:
            verdicts = judge_batch(client, batch)
        except Exception as e:
            print(f"  ! batch {i // BATCH} failed: {e}", file=sys.stderr)
            continue
        for v in verdicts:
            src = by_id.get(v["fragment_id"], {})
            v["date"] = src.get("date")
            v["source"] = src.get("source")
            v["conversation_title"] = src.get("conversation_title")
            v["revisits"] = src.get("revisits", [])
            scored.append(v)
        scored_path.write_text(json.dumps(scored, ensure_ascii=False, indent=2))
        print(f"[curate] scored {min(i + BATCH, len(todo))}/{len(todo)}")

    scored.sort(key=lambda s: s.get("score", 0), reverse=True)
    scored_path.write_text(json.dumps(scored, ensure_ascii=False, indent=2))
    write_review(scored)


def write_review(scored: list[dict]) -> None:
    """Human-readable approval sheet. Set `approve: yes` per fragment to publish."""
    lines = [
        "# Curation review",
        "",
        "For each fragment you want published, change `approve: no` to `approve: yes`.",
        "Then run `python emit_drafts.py`. Everything emits as draft:true — you still",
        "edit and flip `draft:false` per file before it builds.",
        "",
        "⚠️ = privacy flags present; review the quote before approving.",
        "",
    ]
    for s in scored:
        flag = "⚠️ " if s.get("privacy_flags") else ""
        lines += [
            f"## {flag}[{s['score']}/10] {s['title']}",
            f"- fragment_id: `{s['fragment_id']}`  ·  {s['verdict']}  ·  {s['status_guess']}  ·  {', '.join(s['tags'])}",
            f"- source: {s.get('source')}  ·  {s.get('date')}",
            f"- approve: no",
        ]
        if s.get("privacy_flags"):
            lines.append(f"- privacy_flags: {', '.join(s['privacy_flags'])}")
        lines += ["", f"> {s['quote']}", "", s["distillation"], ""]
    (CURATED / "review.md").write_text("\n".join(lines))
    print(f"[curate] wrote {CURATED / 'review.md'} ({len(scored)} fragments)")


if __name__ == "__main__":
    main()
