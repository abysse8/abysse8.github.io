---
title: "Timing is the information a spike-rate code throws away"
date: 2026-08-18
blurb: "I tried to show spike timing beats firing rate — and my first experiment proved the opposite. The real claim is sharper: when a stimulus lives in the spike times, a rate readout gets exactly 0 bits. It's blind, by construction, to information that's physically there."
tags: ["neuroscience", "information-theory", "spikes", "neural-coding"]
hero: /posts/timing.png
code: /posts/timing.py
draft: false
---

There's a slogan in neuroscience I've always liked: *timing is the information, not the rate.* The idea is that a neuron's precise spike times carry more than its average firing rate. I went to confirm it with numbers — and my first experiment proved the opposite. That failure is the interesting part.

## The failed version

I encoded a stimulus $s$ in the **firing rate**: stronger stimulus → higher rate. Then I measured the mutual information (how many bits about $s$ you recover) from two readouts: the total spike **count**, and the **first-spike latency**. Result (left panel): the count wins at every spike budget. Of course it does — I put the information *in the rate*, so the rate readout reads it. "Timing always beats rate" is simply false.

![Left: when the stimulus is encoded in the rate, spike count reads it and timing lags. Right: when it's encoded in the timing, the count readout gets ~0 bits — blind — while timing recovers up to 3.1.](/posts/timing.png)

So the slogan, taken literally, is wrong. But there's a true statement hiding under it, and it's stronger.

## The real claim — rate coding is blind to timing

Now flip it. Encode $s$ in the **spike times** — the mean latency of the spikes shifts with $s$ — and **decouple the count from $s$** (same expected number of spikes regardless of stimulus). Measure the same two readouts (right panel):

- **Count (rate) readout: 0.000 – 0.002 bits.** Zero. The stimulus is right there in the data, and a rate code cannot see any of it.
- **Timing readout: 1.6 → 3.1 bits**, climbing as you get more spikes to average over.

That's the honest, defensible version: not "timing beats rate," but **a rate code is a lossy readout that throws away everything in the temporal pattern.** When the message is written in *when* the spikes arrive, counting them recovers nothing.

## Why it matters

The brain has strong reasons to encode in timing: it's fast (a first spike arrives before you could ever estimate a rate) and sparse (one well-placed spike beats a burst). Wherever it does that, a model that summarizes neurons by their firing rate — which is most models — is **structurally blind** to the code. Not "less accurate." Blind, at zero bits.

And the meta-lesson is the one I keep having to relearn: the slogan felt true, and the first honest experiment killed it. The corrected claim is narrower, checkable, and much harder to argue with.

## From scratch

numpy — both encoding scenarios, both readouts, mutual information by binning. [The script](/posts/timing.py) reproduces both panels.
