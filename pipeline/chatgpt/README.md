# ChatGPT idea-mining funnel → /ideas

Mines the owner's ChatGPT memory DB for genuinely original ideas — from **either**
voice (yours or ChatGPT's) — and turns the best into `/ideas` fragments framed as
honest **spark → crystallization** collaborations.

The DB is **read-only** (owner's memory store). A local gitignored copy lives at
`pipeline/data/chatgpt/memory.sqlite`; override with `CHATGPT_DB=/path`.

## Auth (one-time)

Needs the Anthropic API. Either:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or: install the `ant` CLI and run `ant auth login`
```
All commands below use the pipeline venv: `pipeline/.venv/bin/python`.

## Run the funnel

```bash
cd pipeline/chatgpt
V=../.venv/bin/python

# Stage 1 — LLM segments every conversation into idea-threads (Haiku).
# TEST FIRST on 30 convs, eyeball data/segments.jsonl, then full run.
$V segment.py --limit 30
$V segment.py                 # full ~2,643 convs, resumable, parallel

# Stage 2 — shortlist the top idea-segments (no API).
$V rank.py                    # -> data/shortlist.json

# Stage 3 — deep-extract spark→crystallization per segment (Opus 4.8).
$V extract.py --limit 10      # spot-check first
$V extract.py                 # full shortlist, resumable

# Stage 4 — cluster lineages + write the review sheet (Opus 4.8).
$V cluster.py                 # -> data/curated/{candidates.scored.json, review.md}
```

## Review & publish (human gate)

1. Open `pipeline/data/curated/review.md` (greatest hits at top). For each idea
   worth publishing, change `approve: no` → `approve: yes`. ⚠️ marks privacy flags.
2. Emit drafts:
   ```bash
   cd pipeline
   .venv/bin/python emit_drafts.py                 # skips ⚠️ flagged
   .venv/bin/python emit_drafts.py --allow-flagged # include them after reading
   ```
3. Edit the generated `src/content/ideas/*.md`, flip `draft: true` → `false`,
   then `npm run build`. Fragments render with the spark→crystallization
   disclosure and attribution line.

## Cost & knobs (`config.py`)

- Stage 1 reads ~all threads on Haiku (~$15–25 one-time). Stages 3–4 are Opus,
  bounded to the shortlist (`SHORTLIST_SIZE`, default 250).
- Tune `SEGMENT_KEEP_SCORE`, `SHORTLIST_SIZE`, models (`MODEL_EXTRACT` can be
  `claude-fable-5` for max quality). `RENDER_CHAR_CAP` bounds transcript size.

## Resumability

`segment.py` and `extract.py` append JSONL and skip ids already done — safe to
Ctrl-C and re-run, or run `segment.py` in the background for the full sweep.
