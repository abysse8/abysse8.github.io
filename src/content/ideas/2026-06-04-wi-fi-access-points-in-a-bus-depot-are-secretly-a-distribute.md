---
title: "Wi-Fi access points in a bus depot are secretly a distributed sensor network"
date: 2026-06-04
tags: ["embedded-networking", "edge-computing", "digital-twin", "rf-mesh"]
status: growing
draft: false
attribution: "your question · ChatGPT's synthesis into concrete project directions"
revisits: [2026-06-10]
sources:
  - kind: chatgpt
    date: 2026-06-04
    speaker: you
    role: spark
    quote: "D\\u00e9j\\u00e0, qui r\\u00e9cup\\u00e8re les donn\\u00e9es et qu'est-ce qu'on peut faire avec ?"
  - kind: chatgpt
    date: 2026-06-04
    speaker: chatgpt
    role: crystallization
    quote: "dans un d\\u00e9p\\u00f4t de bus ou syst\\u00e8me embarqu\\u00e9 mobile, \\u00e7a devient quasiment un r\\u00e9seau de capteurs."
---

I'm looking at the access points in a bus depot and realizing they're not just 'WiFi' — they're distributed Linux computers already collecting RSSI, roaming, mesh topology, link quality, and client presence data. My hunch is that in a mobile embedded environment like a depot, this turns into something close to a sensor network: I could reconstruct real topology, vehicle positions, RF dead zones, bus presence times, and network congestion. From there it opens onto digital twin, predictive maintenance, anomaly detection, and even ML that learns 'this RF pattern precedes a mesh failure.' The strongest angle is that it connects RF, networking, embedded, Linux, and system visualization at once — a rare combination. What's unresolved is which concrete project to build first and how cleanly the data can actually be extracted.
