---
title: "A Kalman filter never removes noise — it weighs how much to believe it"
date: 2026-08-14
blurb: "I was stuck thinking a Kalman filter subtracts noise somehow. It doesn't — the update is exactly a precision-weighted average of your prediction and your measurement (verified to 2e-16). The famous gain is just a trust dial. 'Filtering' is belief-weighting."
tags: ["kalman-filter", "estimation", "signal-processing", "bayesian"]
hero: /posts/kalman.png
code: /posts/kalman.py
draft: false
---

For the longest time I couldn't see how a Kalman filter *filters*. The process noise $Q$ and measurement noise $R$ never seem to get subtracted from anything — $Q$ just gets added to a covariance. Where does the noise removal happen?

It doesn't. That's the whole insight: **a Kalman filter never removes noise. It weighs how much to believe each new measurement.**

## What the update actually is

At each step you hold two beliefs, each a Gaussian:
- your **prediction**, $\mathcal{N}(\hat x^-,\,P^-)$ — where the model says the state should be,
- your **measurement**, $\mathcal{N}(z,\,R)$ — where the sensor says it is.

The Kalman update fuses them, and the fusion of two Gaussians is a **precision-weighted average** (precision = 1/variance):

$$\hat x = \frac{\hat x^-/P^- + z/R}{1/P^- + 1/R}.$$

I ran the standard gain-and-update equations and checked them against that formula, step by step. They're identical to **2×10⁻¹⁶** — machine precision. The Kalman gain $K = P^-/(P^-+R)$ isn't subtracting anything; it's the fraction $\tfrac{1/R}{1/P^- + 1/R}$ — the measurement's share of the total precision. "Filtering" *is* precision-weighted fusion.

![Left: the estimate tracks the true state while ignoring the scattered noisy measurements. Right: the gain vs measurement noise — a trust dial from 1 (believe the sensor) to 0 (believe the model).](/posts/kalman.png)

## The gain is a trust dial

The right panel is the gain $K$ as the measurement noise $R$ varies. When the sensor is reliable ($R$ small), $K \to 1$: move all the way to the measurement. When it's noisy ($R$ large), $K \to 0$: barely move, trust the model. $Q$ and $R$ never cancel — they set *where on this dial you sit.*

In the run on the left, $K = 0.13$: the filter steps only **13% of the way** toward each new measurement, because the measurements are noisy relative to how fast the state actually drifts. It looks like it's ignoring the data. It sort of is — and that's the point. The estimate ends up **5.6× more accurate** (mean squared error) than the raw measurements, not by scrubbing noise out, but by *refusing to overreact to a surprise that looks more like sensor noise than real state change.*

## Why this reframing matters

Call it "filtering" and you look for the subtraction that isn't there. Call it what it is — **belief updating under uncertainty** — and every knob makes sense: inflate $Q$ and the filter trusts the model less and chases data harder; inflate $R$ and it clings to its prediction. It's Bayes' rule, running once per timestep, on two Gaussians. The noise was never the enemy to be removed; it was the thing that tells you how much to trust.

## From scratch

Scalar Kalman filter in a dozen lines of numpy, plus the precision-weighted-mean check and the gain sweep. [The script](/posts/kalman.py) reproduces both panels.
