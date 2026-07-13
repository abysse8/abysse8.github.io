---
title: "The bypass capacitor doesn't stabilize the source voltage — it deliberately dest"
date: 2025-02-23
tags: ["analog-electronics", "common-source-amplifier", "bypass-capacitor", "negative-feedback"]
status: growing
domain: embedded
draft: false
attribution: "your misconception surfaced by asking for a critique · corrected and sharpened with ChatGPT"
sources:
  - kind: chatgpt
    date: 2025-02-23
    speaker: you
    role: spark
    quote: "Tell me what's incorrect about this statement using the equations of the amplifier"
  - kind: chatgpt
    date: 2025-02-23
    speaker: chatgpt
    role: crystallization
    quote: "\\( C_3 \\) **does not keep \\( V_S \\) constant for all signals—it changes \\( V_S \\) specifically for AC signals**."
---

I had reasoned that the source bypass capacitor $C_3$ exists to keep $V_S$ constant so the small signal doesn't disturb the DC operating point. The correction is subtle but important: $C_3$ does the opposite for AC signals — it shorts $R_S$ at signal frequencies, letting $V_S$ swing freely. That's the whole point, because it removes the negative feedback term and lifts the gain from $-g_m R_D/(1+g_m R_S)$ up to $-g_m R_D$. So the capacitor preserves DC bias stability while intentionally *increasing* AC fluctuation at the source. The word 'decoupling' names this act of isolating the AC gain path from the DC biasing resistor.
