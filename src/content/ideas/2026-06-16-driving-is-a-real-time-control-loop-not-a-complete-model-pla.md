---
title: "Driving is a real-time control loop, not a complete-model planning problem"
date: 2026-06-16
tags: ["driving", "control-systems", "mental-models", "attention"]
status: growing
domain: meta
draft: false
attribution: "spark: your question · reframe and analogy: ChatGPT"
sources:
  - kind: chatgpt
    date: 2026-06-16
    speaker: you
    role: spark
    quote: "I feel like there's so much information going on, I just don't have time to process it."
  - kind: chatgpt
    date: 2026-06-16
    speaker: chatgpt
    role: crystallization
    quote: "Driving is a real-time control problem, not a planning problem."
---

I kept feeling overwhelmed while driving because I was trying to process everything at once. The insight is that good drivers don't process more — they filter aggressively down to a priority stack: don't hit anything, stay legal, then run a repeating scan loop. My instinct as an engineer is to build a complete model before acting, but driving punishes that; it's a real-time control problem where you observe and correct continuously rather than pre-computing the whole trajectory. Framed as a PID loop, it finally clicks.
