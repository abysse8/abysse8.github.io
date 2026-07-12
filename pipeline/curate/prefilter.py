"""Stage (a): cheap, free heuristic prefilter.

Reads pipeline/data/normalized/*.jsonl, keeps user messages that look like ideas
(not ops chatter), dedupes, and writes pipeline/data/curated/candidates.json for
the LLM judge. Thousands of messages -> low hundreds.

Each candidate carries the user message + a slice of the assistant reply (context
for the judge) and a stable fragment_id = sha1(source+conversation_id+index)[:12].
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingest"))
from schema import NORMALIZED, CURATED, iter_jsonl  # noqa: E402

MIN_LEN = 80
MAX_LEN = 2000
REPLY_CONTEXT_CHARS = 1500

DOMAIN_KEYWORDS = [
    "neuromorph", "spiking", "spike", "stdp", "wavelet", "membrane",
    "transcription", "learning algorithm", "codon", "hebbian", "plasticit",
    "oscillat", "encoding", "backprop", "connectom", "cochlea", "liposome",
    "rs485", "rs-485", "embedded", "fourier", "nyquist", "lagrange",
    "group theory", "hydrodynamic", "excitable", "dendrit", "axon",
]
HYPOTHESIS_PHRASES = [
    "what if", "could we", "could it", "is it possible", "i wonder",
    "hypothesis", "why does", "why do", "why is", "is there a connection",
    "analogous to", "what would happen", "what's the relationship",
    "does this mean", "in theory", "conceptually",
]
# Openers that signal routine ops/debugging, not an idea.
OPS_OPENERS = re.compile(
    r"^\s*(fix|run|install|debug|add|remove|delete|update|refactor|rename|"
    r"why (is|does) (this|my) (error|code|build|test)|npm |pip |git |cd |ls |"
    r"can you (fix|run|add|make it)|please (fix|run|add))",
    re.IGNORECASE,
)
CODEY = re.compile(r"^\s*[$>#]|://|\b\w+\.(py|cpp|tsx?|jsx?|ino|c|h|sh|json|yml)\b|Traceback|Error:")


def _fragment_id(source: str, conv_id: str, idx: int) -> str:
    return hashlib.sha1(f"{source}|{conv_id}|{idx}".encode()).hexdigest()[:12]


def _is_ops_chatter(text: str) -> bool:
    if OPS_OPENERS.match(text):
        return True
    lines = text.splitlines() or [text]
    codey = sum(1 for ln in lines if CODEY.search(ln))
    return codey / max(len(lines), 1) > 0.30


def _has_idea_signal(text: str) -> bool:
    low = text.lower()
    if any(k in low for k in DOMAIN_KEYWORDS):
        return True
    return any(p in low for p in HYPOTHESIS_PHRASES)


def _norm_for_dedupe(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower())


def _token_set(text: str) -> set[str]:
    return set(_norm_for_dedupe(text).split())


def collect() -> list[dict]:
    raw: list[dict] = []
    for path in sorted(NORMALIZED.glob("*.jsonl")):
        for conv in iter_jsonl(path):
            msgs = conv["messages"]
            for i, m in enumerate(msgs):
                if m["role"] != "user":
                    continue
                text = m["text"].strip()
                if not (MIN_LEN <= len(text) <= MAX_LEN):
                    continue
                if _is_ops_chatter(text):
                    continue
                if not _has_idea_signal(text):
                    continue
                reply = ""
                if i + 1 < len(msgs) and msgs[i + 1]["role"] == "assistant":
                    reply = msgs[i + 1]["text"][:REPLY_CONTEXT_CHARS]
                raw.append({
                    "fragment_id": _fragment_id(conv["source"], conv["conversation_id"], i),
                    "source": conv["source"],
                    "conversation_id": conv["conversation_id"],
                    "conversation_title": conv["title"],
                    "date": m.get("ts") or conv.get("date"),
                    "user_text": text,
                    "assistant_context": reply,
                })
    return raw


def dedupe(cands: list[dict]) -> list[dict]:
    """Exact-hash then near-dup (token Jaccard > 0.85 within same source).
    Keep earliest; record later dates as revisits."""
    cands = sorted(cands, key=lambda c: c["date"] or "")
    seen_exact: dict[str, dict] = {}
    kept: list[dict] = []
    for c in cands:
        h = _norm_for_dedupe(c["user_text"])
        if h in seen_exact:
            seen_exact[h].setdefault("revisits", []).append(c["date"])
            continue
        seen_exact[h] = c
        # near-dup scan against kept of same source
        ts = _token_set(c["user_text"])
        dup_of = None
        for k in kept:
            if k["source"] != c["source"]:
                continue
            kt = _token_set(k["user_text"])
            if not kt or not ts:
                continue
            j = len(ts & kt) / len(ts | kt)
            if j > 0.85:
                dup_of = k
                break
        if dup_of:
            dup_of.setdefault("revisits", []).append(c["date"])
        else:
            kept.append(c)
    return kept


def main() -> None:
    CURATED.mkdir(parents=True, exist_ok=True)
    cands = collect()
    print(f"[prefilter] {len(cands)} candidates passed heuristics")
    deduped = dedupe(cands)
    print(f"[prefilter] {len(deduped)} after dedupe")
    out = CURATED / "candidates.json"
    out.write_text(json.dumps(deduped, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[prefilter] wrote {out}")


if __name__ == "__main__":
    main()
