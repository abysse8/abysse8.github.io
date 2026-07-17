# Ideas pipeline

Turns AI-conversation exports into curated "idea fragments" for `/ideas`.
All of `pipeline/data/` is gitignored — raw chats never enter git.

## Flow

```
raw exports ─▶ ingest ─▶ normalized JSONL ─▶ prefilter ─▶ candidates.json
                                                              │
                                          llm_curate ─▶ candidates.scored.json + review.md
                                                              │
                              (you edit review.md: approve: yes)
                                                              │
                                          emit_drafts ─▶ src/content/ideas/*.md (draft:true)
                                                              │
                              (you edit + flip draft:false)  ─▶ builds into /ideas
```

## Run it

```bash
# 0. (optional) drop ChatGPT / claude.ai export zips into pipeline/data/raw/

# 1. Ingest — local sources need no setup; zip sources read from data/raw/
cd pipeline/ingest
python ingest_codex.py
python ingest_claude_code.py
python ingest_chatgpt.py      # no-op if no export present
python ingest_claude_ai.py    # no-op if no export present

# 2. Prefilter (free, heuristic) — tune thresholds in prefilter.py and re-run
cd ../curate
python prefilter.py

# 3. LLM curation (needs ANTHROPIC_API_KEY or `ant auth login`)
python llm_curate.py          # writes candidates.scored.json + review.md

# 4. Review: open pipeline/data/curated/review.md, change `approve: no` → `yes`
#    for the fragments worth publishing.

# 5. Emit drafts (human gate)
cd ..
python emit_drafts.py                  # skips fragments with privacy flags
python emit_drafts.py --allow-flagged  # include flagged ones after you've read them

# 6. Edit the generated src/content/ideas/*.md, flip `draft: true` → `draft: false`,
#    then `npm run build`.
```

## Token-free queue (already-scored ideas)

When ideas are **already scored** by a prior run (e.g. the idea-inventory export),
skip the LLM entirely — no API tokens:

```bash
# 1. Put the scored ideas at  pipeline/data/raw/idea_inventory.json
#    (list of {s: score, d: domain, k: user|both|assistant, i: idea, dt: date, topic})

# 2. Copy the name block and fill in real names (gitignored, local only):
cp pipeline/queue/denylist.example.txt pipeline/data/denylist.txt   # then edit

# 3. Build the review queue (deterministic filters only — no model calls):
python pipeline/queue/build_queue.py            # default: score >= 9, yours only
python pipeline/queue/build_queue.py --min-score 8   # widen the net

# 4. Approve in pipeline/data/curated/review.md, then emit as usual:
python pipeline/emit_drafts.py
```

`build_queue.py` filters: score threshold, `attribution ∈ {user, both}` (never the
assistant's ideas), **denylist hard block**, and dedupe vs already-published
fragments. The denylist is a deterministic third-party name block with **no
override** — enforced again inside `emit_drafts.py`, so a blocked name can never
publish even if approved by mistake.

## Privacy

- `pipeline/data/` is gitignored. Raw exports and normalized transcripts stay local.
- `pipeline/data/denylist.txt` (real names) is gitignored; only the `.example.txt` is tracked.
- The curator flags names/employers/paths/credentials in `privacy_flags`; those
  fragments won't emit without `--allow-flagged`.
- Every emitted fragment is `draft: true`. `getCollection('ideas', …!draft)` keeps
  drafts out of the build. Nothing publishes without a human flipping the flag.

## Adding a source or tuning curation

- New domain keywords / hypothesis phrases: edit `curate/prefilter.py`.
- Curation rubric / voice: edit `curate/prompts/curator_system.txt`.
- Later rooms (Notes, Papers): reuse ingest + prefilter, swap the curator prompt.
