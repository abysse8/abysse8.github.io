---
title: "Model the wiring as a typed spatial multigraph, not a diagram"
date: 2026-06-09
tags: ["graph-modeling", "data-schema", "networkx", "wiring"]
status: growing
draft: false
attribution: "spark: your one-line demand · schema and multigraph framing: ChatGPT"
sources:
  - kind: chatgpt
    date: 2026-06-09
    speaker: you
    role: spark
    quote: "Let’s make an interconnection graph that’s mathematical and precise"
  - kind: chatgpt
    date: 2026-06-09
    speaker: chatgpt
    role: crystallization
    quote: "if the tables generated from the graph are correct, the model is useful. If only the diagram is pretty, it may still be garbage."
---

I want to represent vehicle equipment interconnections as a mathematically precise graph before touching any rendering. The key insight is that a plain graph collapses information — the same two devices connect via power, data, ground, etc. — so I need a typed, attributed, spatial multigraph (a NetworkX MultiDiGraph) where nodes are equipment/zones/connectors and edges carry protocol, cable type, length, and status. The decisive test isn't a pretty picture: it's whether I can generate correct cable and equipment tables from that single graph. Rendering (SVG, Graphviz, Mermaid) then becomes a deterministic export problem downstream. Still open: whether v1 stays equipment-level or goes to connector-pin precision.
