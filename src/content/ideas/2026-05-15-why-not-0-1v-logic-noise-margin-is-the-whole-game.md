---
title: "Why not 0.1V logic? Noise margin is the whole game"
date: 2026-05-15
tags: ["electronics", "noise-margin", "embedded-systems", "signaling"]
status: growing
domain: embedded
draft: false
attribution: "spark: your question · explained and sharpened by ChatGPT"
sources:
  - kind: chatgpt
    date: 2026-05-15
    speaker: you
    role: spark
    quote: "Why do we not use 0.1 volt logic? What's the big thing stopping us from doing that?"
  - kind: chatgpt
    date: 2026-05-15
    speaker: chatgpt
    role: crystallization
    quote: "A huge amount of engineering is really:
moving information reliably through imperfect physics."
---

I wanted to know what physically stops us from using tiny logic swings like 0.1V to save power. The answer is noise margin: real systems have thermal noise, ground bounce, crosstalk, and EM interference, so if your logic '1' and '0' are only 0.1V apart, a small ground shift makes them indistinguishable. CPUs do push voltages down (5V→3.3V→~1V) because dynamic CMOS power scales like $V^2$, but they only get away with it because distances are microscopic and grounds are tightly controlled. Over long noisy cables you instead go differential (RS485, measuring A−B) so common-mode noise cancels. The deeper lesson is that a lot of engineering is really about moving information reliably through imperfect physics.
