---
title: "Teaching a photodiode array to be a camera by learning the inverse mapping"
date: 2026-05-18
tags: ["embedded", "optics", "machine-learning", "sensors"]
status: growing
domain: embedded
draft: false
attribution: "spark: you · sharpened and scoped with ChatGPT"
sources:
  - kind: chatgpt
    date: 2026-05-18
    speaker: you
    role: spark
    quote: "It’d definitely be cool to have an array of photodiodes next to a sensor and teach the photodiode array to become a caméra by learning"
  - kind: chatgpt
    date: 2026-05-18
    speaker: chatgpt
    role: crystallization
    quote: "I built a low-resolution optical sensor array and trained the inverse mapping from raw analog readings to spatial state."
---

I want to build a 'camera' not by imaging optics but by learning the mapping from raw analog photodiode voltages to spatial state. Instead of reconstructing pixels, an array of cheap photodiodes feeds a small model that learns to infer position, shape, or motion of an object. The insight is to start in 1D — one row of 4-8 photodiodes, a moving shadow, and a model trained on labeled readings — rather than jumping to a full 2D sensor with all its wiring and calibration. It's a fusion of embedded hardware, optics, signal processing, and ML: the sensor becomes a camera through learning, not lenses. Open question is how far the learned inverse mapping scales toward real image reconstruction.
