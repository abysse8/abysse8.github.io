"""Stage 4: cluster fragments into idea-lineages, then write the review sheet.

The owner revisits ideas across many conversations over years — merge those into
one fragment (canonical statement + revisit dates + all sources). Then rank by
originality and emit the human-review artifacts the existing gate consumes:
  pipeline/data/curated/candidates.scored.json  (machine)
  pipeline/data/curated/review.md               (human: set approve: yes)

Usage: python cluster.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import anthropic

from config import DATA, CURATED, MODEL_CLUSTER

SYSTEM = (Path(__file__).parent / "prompts" / "cluster_system.txt").read_text()

SCHEMA = {
    "type": "object",
    "properties": {
        "clusters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "member_indexes": {"type": "array", "items": {"type": "integer"}},
                    "canonical_index": {"type": "integer"},
                    "reason": {"type": "string"},
                },
                "required": ["member_indexes", "canonical_index", "reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["clusters"],
    "additionalProperties": False,
}


def iso(ts) -> str | None:
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).date().isoformat()
    except Exception:
        return None


def load_fragments() -> list[dict]:
    src = DATA / "fragments.jsonl"
    if not src.exists():
        raise SystemExit("Run extract.py first — no fragments.jsonl.")
    return [json.loads(l) for l in src.read_text().splitlines() if l.strip()]


def cluster(client, frags: list[dict]) -> list[list[int]]:
    listing = "\n".join(
        f"#{i} [{iso(f.get('date')) or '?'}] {f['title']} — {f['distillation'][:120]}"
        for i, f in enumerate(frags)
    )
    resp = client.messages.create(
        model=MODEL_CLUSTER,
        max_tokens=8000,
        system=SYSTEM,
        messages=[{"role": "user", "content": listing}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}, "effort": "medium"},
    )
    text = next(b.text for b in resp.content if b.type == "text")
    clusters = json.loads(text)["clusters"]
    # Validate coverage; anything the model dropped becomes its own solo cluster.
    seen = set()
    groups = []
    for cl in clusters:
        members = [i for i in cl["member_indexes"] if 0 <= i < len(frags) and i not in seen]
        if not members:
            continue
        canon = cl["canonical_index"] if cl["canonical_index"] in members else members[0]
        seen.update(members)
        groups.append((canon, members))
    for i in range(len(frags)):
        if i not in seen:
            groups.append((i, [i]))
    return groups


def merge(frags: list[dict], groups) -> list[dict]:
    out = []
    for canon, members in groups:
        base = frags[canon]
        others = [frags[m] for m in members if m != canon]
        dates = sorted(d for d in (iso(frags[m].get("date")) for m in members) if d)
        privacy = sorted({p for m in members for p in (frags[m].get("privacy_flags") or [])})
        sources = [{
            "kind": "chatgpt",
            "conv_id": base["conv_id"],
            "date": iso(base.get("date")),
            "spark": base["spark"],
            "crystallization": base["crystallization"],
        }]
        for o in others:
            sources.append({
                "kind": "chatgpt", "conv_id": o["conv_id"], "date": iso(o.get("date")),
                "spark": o["spark"], "crystallization": o["crystallization"],
            })
        out.append({
            "fragment_id": base["segment_id"],
            "title": base["title"],
            "distillation": base["distillation"],
            "attribution": base["attribution"],
            "tags": base["tags"][:4],
            "status": base["status"],
            "unresolved": base.get("unresolved", ""),
            "domain": base.get("domain"),
            "date": iso(base.get("date")) or (dates[-1] if dates else None),
            "revisits": [d for d in dates if d != (iso(base.get("date")))],
            "span": {"first": dates[0], "last": dates[-1]} if dates else None,
            "score": max(frags[m].get("is_original", 0) for m in members),
            "n_sources": len(members),
            "privacy_flags": privacy,
            "sources": sources,
        })
    out.sort(key=lambda f: (f["score"], f["n_sources"]), reverse=True)
    return out


def write_review(frags: list[dict]) -> None:
    CURATED.mkdir(parents=True, exist_ok=True)
    (CURATED / "candidates.scored.json").write_text(json.dumps(frags, ensure_ascii=False, indent=2))
    lines = [
        "# Ideas — review (greatest hits at top)",
        "",
        "Set `approve: yes` on the fragments you want published, then run",
        "`python ../emit_drafts.py` (add `--allow-flagged` to include ⚠️ ones).",
        "Everything emits as draft:true; edit and flip draft:false per file to publish.",
        "",
    ]
    for f in frags:
        flag = "⚠️ " if f["privacy_flags"] else ""
        span = f"{f['span']['first']}→{f['span']['last']}" if f.get("span") else f.get("date")
        lines += [
            f"## {flag}[{f['score']}/10] {f['title']}",
            f"- fragment_id: `{f['fragment_id']}`  ·  {f['status']}  ·  {', '.join(f['tags'])}  ·  {f.get('domain','')}",
            f"- {span}  ·  {f['n_sources']} conversation(s)  ·  {f['attribution']}",
            "- approve: no",
        ]
        if f["privacy_flags"]:
            lines.append(f"- privacy_flags: {', '.join(f['privacy_flags'])}")
        sp, cr = f["sources"][0]["spark"], f["sources"][0]["crystallization"]
        lines += [
            "",
            f"> **{sp['speaker']} (spark):** {sp['quote']}",
            f"> **{cr['speaker']} (crystallized):** {cr['quote']}",
            "",
            f["distillation"],
            "",
        ]
    (CURATED / "review.md").write_text("\n".join(lines))
    print(f"[cluster] {len(frags)} lineage fragments -> {CURATED/'review.md'}")


def main() -> None:
    frags = load_fragments()
    print(f"[cluster] {len(frags)} extracted fragments")
    client = anthropic.Anthropic()
    groups = cluster(client, frags)
    merged = merge(frags, groups)
    print(f"[cluster] merged into {len(merged)} lineages")
    write_review(merged)


if __name__ == "__main__":
    main()
