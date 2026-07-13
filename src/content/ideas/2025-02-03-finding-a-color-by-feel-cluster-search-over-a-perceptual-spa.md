---
title: "Finding a color by feel: cluster search over a perceptual space"
date: 2025-02-03
tags: ["color-search", "clustering", "k-means", "human-perception"]
status: growing
domain: meta
draft: false
attribution: "your problem framing · method proposed and sharpened by ChatGPT"
sources:
  - kind: chatgpt
    date: 2025-02-03
    speaker: you
    role: spark
    quote: "cluster search kind of sounds like what im looking for. Can you describe both your options to me and write the code added with cluster search"
  - kind: chatgpt
    date: 2025-02-03
    speaker: chatgpt
    role: crystallization
    quote: "Instead of a strict binary split, we **cluster similar colors** together using **k-means clustering** or **octree color quantization**.
- We show the user **two colors** from the most relevant cluster instead of picking from a linear list.
- Over time, the search space shrinks to a smaller set of the closest possible matches."
---

I want to help someone pin down a specific color without knowing its values — by repeatedly choosing between two options until we converge. My hunch is that a plain binary search fails because colors have no natural linear order to split on. Clustering (k-means or octree quantization) is more adaptive: group the 32,768 colors, show two representatives, and shrink the search space based on which one feels closer. It's better suited to human perception than a strict linear split. Still open: how many clusters to use, and how to run the interaction outside a GUI environment.
