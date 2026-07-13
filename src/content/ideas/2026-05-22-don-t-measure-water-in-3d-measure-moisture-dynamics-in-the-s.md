---
title: "Don't measure water in 3D — measure moisture dynamics in the substrate"
date: 2026-05-22
tags: ["sensor-networks", "soil-moisture", "diy-hardware", "data-modeling"]
status: growing
draft: false
attribution: "spark: your question · reframing and mechanical fix from ChatGPT"
sources:
  - kind: chatgpt
    date: 2026-05-22
    speaker: you
    role: spark
    quote: "j'ai envie de dire, en trois dimensions, et je ne pense pas que les capteurs d'humidité capacitifs puissent avoir autant de précision, mais en général, comment je fais quand j'ai beaucoup de capteurs et que j'ai besoin de synchroniser leurs données"
  - kind: chatgpt
    date: 2026-05-22
    speaker: chatgpt
    role: crystallization
    quote: "Ne vise pas “voir l’eau en 3D”. Vise “observer la dynamique d’humidité dans le substrat”. C’est réaliste, mesurable, et défendable techniquement."
---

I want to place multiple moisture sensors around one plant and reconstruct how water is absorbed, almost like a 3D map. The realistic framing is that cheap capacitive sensors can't give a true tomography — so instead of chasing precision, I should treat each timed reading across all sensors as a synchronized 'snapshot,' log positions plus timestamps, and use crude distance-weighted interpolation to show layers (surface/mid/deep). The real bottleneck isn't the model, it's mechanical: my long capacitive probes bury their electronics, so I should insert sensors laterally through the pot with electronics kept outside. Calibration per-sensor (dry/wet/saturated) is what keeps the map honest.
