---
title: "Chromatin as a state machine: modeling gene access as nucleosome states"
date: 2025-06-10
tags: ["chromatin", "computational-biology", "state-machine", "gene-regulation"]
status: growing
domain: bio
draft: false
attribution: "your paper and framing goal; ChatGPT's synthesis into a state-machine simulation model"
sources:
  - kind: chatgpt
    date: 2025-06-10
    speaker: you
    role: spark
    quote: "Reading this paper now. Can you give me a rundown"
  - kind: chatgpt
    date: 2025-06-10
    speaker: chatgpt
    role: crystallization
    quote: "Think of TFs as control agents that can send “modify region” commands to the chromatin state machine."
---

I'm reading Kornberg & Lorch's nucleosome review and want to translate its biology into a computational model. My hunch is that chromatin regulation can be captured as a state machine: each nucleosome holds a discrete state (wrapped, loosened, evicted) plus a histone-tail modification bitmask, and transcription factors act as agents that read local accessibility and issue 'modify region' commands by recruiting HATs or remodelers. Gene expression then becomes a boolean function of promoter accessibility. What's unresolved is whether this discrete abstraction captures enough of the real dynamics — charge neutralization, fiber-level coiling, ATP-driven sliding — to be predictive rather than just illustrative.
