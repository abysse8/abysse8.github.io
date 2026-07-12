# Homepage Redesign Plan — abysse8.github.io

Goal: a visitor thinks **"this engineer builds difficult systems"** within 5 seconds.
Aesthetic: premium Apple/Vercel, dark, minimal but memorable. Lighthouse ≥ 95 on all four scores.

Live prototype of the target design: see the Claude artifact from this session (`v1-terminal-hero`).

---

## 0. Bugs in the current site (fix regardless)

1. **Broken hero video** — `index.md` references `/assets/scrolling-terminal.webm`, but the file
   is committed as `assets/.scrolling-terminal.webm` (hidden dotfile). The background video 404s
   in production. The redesign *replaces* it with a typed-terminal component (same soul, ~0 KB).
2. Two project links in `projects.md` point at `github.com/yourusername/...` (template leftovers).
3. `cv.md`, `notes.md`, `papers.md`, `hall-of-fame.md`, `homework.md`, `ideas.md` are 1-byte
   placeholders — the homepage links to eight rooms, six of which are empty. Recruiter poison.
   Either fill them or mark them "opening soon" in the rooms grid until they have content.

---

## 1. New homepage structure (top → bottom)

| # | Section | Why it exists |
|---|---------|---------------|
| 1 | Sticky blur nav | Orientation + one recruiter CTA always visible ("For Employers"). |
| 2 | Hero: headline + typed terminal | The thesis. Headline states positioning; the terminal *shows* real work (RS485 sniffing, PlatformIO builds, the Gemini pipeline) instead of claiming it. Replaces the broken bg video. |
| 3 | Proof strip (4 stats) | Recruiters scan numbers. "3 protocols reverse-engineered · <10 ms PID · 17 production units · 20 min → 30 s" are concrete difficulty proof. |
| 4 | Selected Work — bento grid | 6 projects, ESP32 Display Panel featured wide. Bento signals modern taste; the content signals depth. |
| 5 | Research direction | The neuromorphic statement, tightened to one paragraph. Differentiator vs. every other embedded portfolio. Links to /ideas for depth. |
| 6 | Exhibition Rooms — 8-cell grid | **Preserves all existing content/links** (notes, papers, hall of fame, projects, presentations, homework, ideas, ask). Museum personality kept, presented as a quiet numbered grid. |
| 7 | Contact CTA + footer | Explicit ask: "Hiring for hard problems?" + email + CV. Footer keeps the caffeine/chaos line — it's personality worth keeping. |

Nothing from the old homepage is deleted: the video idea became the terminal, the two big
buttons became nav CTA + research link, the rooms list became the grid, the "What is this?"
museum text became the Exhibits section intro.

## 2. Component list (reuse, don't invent)

| Section | Open-source source | Adaptation |
|---|---|---|
| Nav | shadcn/ui `navigation-menu` + Origin UI navbar patterns | Strip to 4 links + CTA; `backdrop-blur` + `bg-background/70`; border-b hairline. |
| Terminal | **Magic UI `Terminal`** (`magicui.design/docs/components/terminal`) | Replace demo content with real commands from the repos; loop once, no sound; honor `prefers-reduced-motion` (render final state instantly). |
| Hero text reveal | **Motion Primitives `TextEffect`** (fade-up per-word) | `preset="fade-in-blur"`, `speedReveal=1.5`, run once on load only. |
| Hero background | Magic UI `Grid Pattern` (or Aceternity "Grid and Dot Backgrounds") | Pure CSS gradient grid + radial mask; opacity 0.25 — must stay subliminal. |
| Proof strip | Magic UI `NumberTicker` | Animate on first in-view only; `font-variant-numeric: tabular-nums`; skip animation under reduced motion. |
| Bento grid | **Magic UI `Bento Grid`** | 3-col, featured card `col-span-2`; kill spotlight/glow effects — keep hover to `translateY(-2px)` + border lighten. |
| Project cards | shadcn/ui `Card` + `Badge` | Badges as mono stack chips; whole card clickable with a single stretched link (a11y: one tab stop per card). |
| Scroll reveals | **Motion Primitives `InView`** | 14 px rise + fade, 0.6 s, once; disable under reduced motion. |
| Rooms grid | Origin UI list/grid patterns (1px-gap grid trick) | `gap-1px` with border-color background = hairline dividers, Vercel-style. |
| Contact | shadcn/ui `Button` variants | Primary = white on black (Vercel inversion), ghost = hairline border. |

Explicitly rejected: Aceternity 3D cards, spotlight/beam effects, marquees, cursor followers —
gimmick risk, Lighthouse cost, and they contradict "difficult systems" seriousness.

## 3. Implementation order

1. **Content fixes** (broken video ref, `yourusername` links, placeholder pages) — ship today on Jekyll.
2. **Scaffold** Astro + React islands + Tailwind, deploy via GitHub Actions to Pages (keep Jekyll until parity).
3. **Static shell**: tokens, nav, footer, section scaffolding (no animation yet).
4. **Hero** headline + CTAs, then Terminal island.
5. **Bento grid** with all 6 projects from a single `site.config.ts` data file.
6. **Proof strip, research, rooms, contact** (mostly static HTML — zero JS).
7. **Animation pass**: InView reveals, NumberTicker, reduced-motion audit.
8. **Lighthouse pass**: font subsetting, `astro build` output audit, preload checks. Target ≥ 95 all four.
9. Swap Pages source from Jekyll to Astro build; keep old URLs (`/notes.html` etc.) working.

## 4. Code architecture

```
/
├─ astro.config.mjs          # static output, site: abysse8.github.io
├─ src/
│  ├─ config/site.ts         # ALL content: projects, stats, rooms, links (single source of truth)
│  ├─ styles/tokens.css      # palette, spacing, type scale (CSS custom properties)
│  ├─ layouts/Base.astro     # <head>, fonts, nav, footer
│  ├─ pages/index.astro      # homepage — composes sections, ~zero client JS itself
│  │  └─ (notes|papers|...).astro   # existing rooms, migrated from .md
│  └─ components/
│     ├─ Terminal.tsx        # client:visible island (adapted Magic UI)
│     ├─ NumberTicker.tsx    # client:visible island (Magic UI)
│     ├─ InView.tsx          # tiny IntersectionObserver wrapper (Motion Primitives pattern)
│     ├─ BentoCard.astro     # static — no JS needed
│     └─ RoomsGrid.astro     # static
└─ .github/workflows/deploy.yml
```

Principle: **islands only where motion demands JS**. Terminal + ticker + reveals ≈ 15 KB gzipped
total client JS. Everything else is prerendered HTML/CSS → LCP is the headline text, CLS ≈ 0.

## 5. Animation plan (subtle, orchestrated, once)

- Page load: hero eyebrow → headline → sub → CTAs stagger in (fade + 14 px rise, 0.6 s, ~80 ms stagger).
- Terminal starts typing ~300 ms after hero settles (26–56 ms/char); runs once, cursor keeps blinking.
- Scroll: each section reveals once at 12% visibility. No parallax, no scroll-jacking.
- Hover: cards rise 2 px + border lightens (0.2 s); links color-shift only.
- `prefers-reduced-motion`: reveals render instantly, terminal prints final state, ticker shows final number.

## 6. Typography

- Display/body: **Geist** (Vercel, OFL) — self-hosted via `@fontsource` or `astro-font`, weights 400/500/650/700 subset to latin. Prototype uses the SF system stack (also acceptable: zero payload).
- Character/data face: **Geist Mono** — eyebrows, stats, chips, terminal, room numbers.
- Scale: 12.4 (mono labels) / 14.4 / 16 body / 17.6 sub / 24–32 h2 (clamp) / 35–54 h1 (clamp).
- H1 `letter-spacing: -0.025em`, `text-wrap: balance`. Mono labels `+0.08em`, uppercase.
- Body ≤ 65ch; hero sub ≤ 46ch.

## 7. Spacing system

4 px base. Steps: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96 / 128.
Section rhythm: 96 px between sections (64 on mobile), 48 heading→content, 16 card gaps, 24 card padding.
Container: `max-width: 1100px`, 24 px side padding. Sibling spacing via flex/grid `gap` only.

## 8. Color palette (dark, committed)

| Token | Hex | Role |
|---|---|---|
| `--bg` | `#0A0A0C` | Ground (near-black, slight cool) |
| `--surface` | `#101014` | Cards, terminal |
| `--surface-2` | `#15151A` | Featured card gradient top |
| `--border` | `#212127` | Hairlines |
| `--border-strong` | `#2E2E36` | Hover borders, ghost buttons |
| `--text` | `#EDEDF0` | Headings, primary text |
| `--muted` | `#9A9AA3` | Body copy |
| `--faint` | `#6B6B75` | Captions, chips |
| `--accent` | `#E8A33D` | Amber phosphor — eyebrows, prompt, cursor, room numbers |
| `--ok` | `#7FBF7F` | Terminal success lines only |

One accent, used small (≤ 5% of any viewport). Contrast: all text pairs ≥ WCAG AA on their grounds
(muted on bg = 7.0:1, faint reserved for ≥ 0.75rem captions). Buttons invert (white bg / black text).

## 9. Accessibility checklist

- Landmarks: `header/nav/main/section/footer`; `aria-label` on both navs.
- Terminal is `aria-hidden` (decorative); its facts are restated in the proof strip as real text.
- One tab stop per card (stretched link), visible `:focus-visible` ring in accent.
- Reduced motion fully honored; `color-scheme: dark` set; all iframes get `title` attrs (presentations page).
