---
title: "The mean said 28 ms. Under load, the tail said 76."
date: 2026-09-01
blurb: "Before I could argue that a drone needs an FPGA, I had to measure what the CPU actually costs. The average was honest. The worst case was not — and for a real-time loop, the worst case is the only number that matters."
tags: ["fpga", "real-time", "embedded", "latency", "measurement"]
draft: true
---

I'm building a drone with a Kria KV260 riding on top — an FPGA board — and I kept telling people the FPGA was justified because it's *more deterministic* than a CPU. It's the kind of thing everyone repeats. So before I put it on my CV, I did the thing I'm bad at: I stopped arguing the architecture and measured.

The result embarrassed me twice. First it proved me wrong. Then it proved me right — but for a different reason than I'd been saying.

## The rule I forced myself to write first

The failure mode I fall into is producing a *diagram* instead of a *number*. So I wrote the falsifier before touching the board:

> The FPGA is justified only if its worst-case latency is **bounded** and lower than the CPU's by a margin that matters for control — say a 20 ms loop budget. If the CPU's worst case already fits with room to spare, the FPGA isn't justified for this job, and I should say so.

If I couldn't finish that sentence, I had a topic, not a claim.

## The experiment

One honest, boring operation: a 3×3 **Sobel** edge filter — the cheapest useful piece of computer vision — on a fixed 1920×1080 frame. Run it 1000 times, time every single run, and report not just the mean but the **worst case** and the **jitter** (standard deviation). Compiled `-O2`, run on the Kria's ARM Cortex-A53 cores.

Then run it twice: once on an idle core, once with all four cores pinned busy — because a real companion computer is *never* idle. It's running the network stack, the camera pipeline, logging, the OS. The idle number is a fantasy; the loaded number is the truth.

## What the numbers said

| | idle core | 4 cores loaded |
|---|---|---|
| mean | 28.4 ms | 36.1 ms |
| best | 28.1 ms | 28.1 ms |
| **worst** | 30.2 ms | **76.5 ms** |
| p99 | 28.7 ms | 72.2 ms |
| **jitter (σ)** | 0.12 ms | **12.3 ms** |

**Where I was wrong:** idle, the CPU is *beautifully* deterministic. Jitter of 0.12 ms, worst case barely 7% above best. My repeated line — "the FPGA wins because the CPU jitters" — is just false when the CPU has a core to itself. The measurement caught me overclaiming.

**Where I was right, but hadn't earned it:** put the system under load and the mean barely moves (28 → 36 ms) while the **tail detonates**. Worst case more than doubles to 76 ms. Jitter grows *a hundredfold*. One percent of frames blow past 72 ms — nearly 4× a 20 ms deadline.

## The number that actually decides it

For a hard real-time control loop you don't get to budget the mean. A late frame isn't averaged away — it's a missed deadline, and the aircraft doesn't care that the other 99 frames were fine. You budget the **worst case**.

And the CPU's worst case is **unbounded**: it tracks whatever else the system is doing. There is no line I can write that says "this will never take longer than X ms," because X depends on the OS scheduler, on the other threads, on load I don't control. That's not a tuning problem. It's structural — the CPU is *shared*, and sharing means contention, and contention means an open-ended tail.

That is the real reason to reach for the FPGA, and it's narrower and more honest than "it's more deterministic." The programmable logic isn't shared with the scheduler. The same filter, built as a streaming pipeline in the fabric, takes a **fixed number of clock cycles** — the same whether the CPU is asleep or on fire. Its worst case has a *ceiling*, and I can write the ceiling down.

That's the whole argument for putting an FPGA in a real-time loop, compressed to one line: **not lower latency on average — a worst case you can bound.**

## What I have *not* done yet

I owe you the other half of the table, and I'm not going to pretend I have it. I measured the CPU. I have not yet built the Sobel as an HLS kernel and measured it on the fabric — that's a Vitis toolchain weekend I haven't spent. So the honest state is:

| | worst case | jitter | bounded? |
|---|---|---|---|
| CPU (loaded) | 76.5 ms | 12.3 ms | **no** — grows with load |
| FPGA (PL) | *pending* | *pending* | *the claim to test* |

Part 2 is that bottom row: implement it, run it under the same load, and see whether the fabric holds flat while the CPU thrashes. If it does, the falsifier is satisfied and I have a real comparison. If the fabric's latency is fine but the CPU's loaded worst case *also* fit the budget with margin — then I was wrong about needing the FPGA for this, and I'll write that post instead.

Either way the number decides, not the diagram. That was the point.
