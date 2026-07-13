---
title: "Why don't two CAN nodes short-circuit when both assert a dominant bit?"
date: 2026-05-11
tags: ["can-bus", "electronics", "embedded-systems", "arbitration"]
status: growing
domain: embedded
draft: false
attribution: "your question, explained by ChatGPT"
sources:
  - kind: chatgpt
    date: 2026-05-11
    speaker: you
    role: spark
    quote: "What if two nodes were trying to send a dominant plus and maybe they're not exactly adding two volts? Doesn't that then create like a short circuit almost?"
  - kind: chatgpt
    date: 2026-05-11
    speaker: chatgpt
    role: crystallization
    quote: "CAN nodes are not “forcing a voltage” onto the line like ideal voltage sources fighting each other."
---

I got stuck on what looked like a physical contradiction in CAN bus: if a dominant bit means raising CAN_H and lowering CAN_L off the 2.5V idle, wouldn't two nodes asserting slightly different voltages fight each other like clashing power supplies and short out? The resolution is that CAN transceivers aren't ideal voltage sources — they're current-limited, open-drain-like drivers built so multiple nodes can assert dominant simultaneously without damage. The bus only cares whether the differential crosses a threshold (~0.9V), not the exact value, so 1.8V and 2.2V decode identically. Dominant physically overrides recessive, which is also what makes nondestructive arbitration work: a node transmitting recessive but reading dominant simply backs off. The dangerous case — one device driving hard HIGH against another driving hard LOW — is exactly what the driver architecture avoids.
