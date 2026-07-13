---
title: "CoverAI should be a candidate profile agent, not a CV generator"
date: 2026-05-03
tags: ["product-design", "autofill", "job-applications", "data-model"]
status: mature
domain: meta
draft: false
attribution: "spark: you · architecture and framing sharpened by ChatGPT"
revisits: [2026-05-04]
sources:
  - kind: chatgpt
    date: 2026-05-03
    speaker: you
    role: spark
    quote: "I want CoverAi to autofil information about the user, that’s also a pain in the process that is slow. When pages have multiple sub pages to fill in like a ensemble of sécurité Check points. That’s not it, at all"
  - kind: chatgpt
    date: 2026-05-03
    speaker: chatgpt
    role: crystallization
    quote: "CoverAI should not only be a CV generator. It should become a **candidate profile agent**."
---

I realized the real pain in job applications isn't generating a CV — it's repeatedly filling structured forms across ugly multi-page recruitment portals with their security checkpoints and screening questions. So CoverAI should store a structured profile once and use it to intelligently fill forms, cover letters, and screening questions. The key insight is that fields split into three tiers: safe fields to autofill, generated fields to suggest-and-review, and sensitive/legal fields that must require manual confirmation. The single source of truth becomes a canonical candidate profile in JSON that CV generation, matching, and autofill all pull from. What's unresolved is the actual profile schema and field-mapping rules, which need defining before any coding.
