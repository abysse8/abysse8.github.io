---
title: "MQTT should be the coordination layer, not the nervous system"
date: 2026-05-08
tags: ["distributed-systems", "mqtt", "industrial-control", "embedded"]
status: mature
domain: embedded
draft: false
attribution: "your project instinct, structured and sharpened by ChatGPT"
revisits: [2026-04-26, 2026-04-27, 2026-05-15, 2026-05-15]
sources:
  - kind: chatgpt
    date: 2026-05-08
    speaker: you
    role: spark
    quote: "I want my devices to communicate"
  - kind: chatgpt
    date: 2026-05-08
    speaker: chatgpt
    role: crystallization
    quote: "Your MQTT bus should not try to become the nervous system for every tiny control signal.

It should be the coordination layer."
---

My hunch is that a distributed device architecture becomes 'serious' only when you stop treating every message as equal. Real-time control (motor loops, safety stops) has to stay local and deterministic, while MQTT should carry coordination and telemetry — jobs, states, capabilities — not raw control signals like 'set PWM to 143.' The key is explicit contracts: defined message types, required fields, allowed states, timeout and failure behavior. Devices should announce capabilities and expose state machines (idle/busy/error/etc.) rather than being hardcoded together. AI fits as a suggester on top: AI suggests, PLC verifies, machine executes — never AI controlling machines directly.
