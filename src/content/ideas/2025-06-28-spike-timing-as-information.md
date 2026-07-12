---
title: "Timing is the information, not the rate"
date: 2025-06-28
tags: [neuromorphic, spiking, signal-processing]
status: mature
draft: false
sources:
  - kind: chatgpt
    date: 2025-06-28
    quote: "How does timing work in spiking neurons — is the information in the rate or in the delay between spikes?"
---

Rate coding is the comfortable story: count spikes in a window, call it a number.
But the biology keeps insisting the *delay between spikes* is the channel. If a
neuron fires at time $t_i$, the inter-spike interval $\Delta t = t_{i} - t_{i-1}$
carries more bits per joule than the rate ever could, because a single
well-placed spike substitutes for a whole burst. This reframes STDP not as a
learning rule bolted onto rate models, but as the *native* operation of a
timing-first substrate. The design consequence for neuromorphic hardware: stop
budgeting for high firing rates and start budgeting for precise clocks.
