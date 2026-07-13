---
title: "Stop asking where an FPGA fits — ask what breaks on a CPU"
date: 2026-05-14
tags: ["fpga", "hardware-acceleration", "systems-design", "determinism"]
status: growing
draft: false
attribution: "your intuition, reframed and sharpened by ChatGPT"
sources:
  - kind: chatgpt
    date: 2026-05-14
    speaker: chatgpt
    role: spark
    quote: "Your intuition about defect detection and navigation is correct, but it is only one slice."
  - kind: chatgpt
    date: 2026-05-14
    speaker: chatgpt
    role: crystallization
    quote: "You should stop thinking:
“Where do I insert an FPGA?”

And instead ask:
“What subsystem becomes impossible or inefficient on a CPU?”"
---

I've been thinking about FPGAs as fancy hobby boards, but the real reframe is that an FPGA doesn't run code fast — it physically builds a custom data path. The right engineering question isn't 'where do I insert an FPGA?' but 'what subsystem becomes impossible or inefficient on a CPU?' That reframe explains why the hard, valuable problem in industry is usually not the AI model but getting synchronized, clean, low-latency data into it — which is exactly what FPGAs do across radar, machine vision, SDR, ultrasound, and HFT. My KV260 makes more sense seen as a reconfigurable hardware accelerator attached to Linux rather than a tiny computer with GPIO. What's unresolved is which specific subsystem in my own projects actually clears that 'impossible on CPU' bar.
