---
title: "Falling is your clock taking the longest path; curvature is what falling can't remove"
date: 2026-10-14
blurb: "Clocks run slower lower down (derived from a rocket, no gravity). Maximise a thrown ball's wristwatch time and the fall comes out (path error 4e-8). Uniform g isn't curvature; tides are. Their trace is zero in vacuum and −4πGρ in matter: that's the field equation."
tags: ["physics", "relativity", "geometry", "numerics"]
hero: /posts/spacetime.png
code: /posts/spacetime.py
draft: false
---

"Mass curves spacetime and curvature tells things how to move" is a slogan. Here it is as four computations, plus the honest answer to "why does mass curve spacetime".

## 1. Clocks lower down run slower, from a rocket alone

No gravity anywhere. A rocket accelerates at $g$. Someone on the floor sends light pulses up to the ceiling, height $h$ above. Each pulse travels while the ceiling speeds away, so pulses arrive spread out. Solving the light-ray intersections in special relativity (units $c=1$, $g = 0.1$):

| | spacing ratio, measured | predicted |
|---|---|---|
| up 1 | 1.1000000000 | $1 + gh$ = 1.1 |
| up 2 | 1.2000000000 | 1.2 |
| down 1 | 0.9090909091 | $1/(1+gh)$ |

Einstein's **equivalence principle**: standing on Earth is locally indistinguishable from accelerating in a rocket. So on Earth, clocks at the top tick faster than clocks at the bottom by $gh/c^2$. For the 22.5 m Harvard tower: $2.46\times10^{-15}$. Pound & Snider (1965) measured it: 0.9990 ± 0.0076 of the prediction.

## 2. The falling path is the one whose clock shows the most time

Throw a ball up, catch it 10 time-units later. Of all paths between those two events, which one does it take? Compute the wristwatch (proper) time of each path,

$$\tau = \int \sqrt{(1 + gz)^2\,dt^2 - dz^2},$$

where the first term is "clocks higher up tick faster" and the second is "moving clocks tick slower". Maximise $\tau$ numerically over 199 free heights, starting from a deliberately wrong bump:

- $g = +0.02$: max height **0.250208**; exact free fall 0.250208; Newton's $gT^2/8 = 0.25$. Max path error $4\times10^{-8}$.
- $g = 0$: the bump flattens to height $10^{-28}$. No clock gradient, no fall.
- $g = -0.02$ (clocks faster *below*): the path dips. Gravity points toward slow clocks.

Scale the true path by a factor $a$: too low ($a<1$) and the clock sits where time is slow; too high ($a>1$) and it pays for the speed needed to get there. Peak at $a = 1.00$. **Falling is not a force acting; it is the path of maximum elapsed time.** Newton's parabola is the slow-speed limit.

This is real engineering. GPS clocks at 20 200 km altitude run fast by **45.7 µs/day** (height) and slow by **7.2 µs/day** (speed): net **+38.5 µs/day** (Ashby 2003). Uncorrected, that is 11.5 km of position error per day.

## 3. A uniform pull is not curvature

Section 2 used a *uniform* clock gradient, and that is not curvature yet. A falling elevator in a uniform field feels nothing at all; the effect is removed by choosing to fall. Computed: tidal tensor of a uniform 9.81 m/s² field = 0 exactly.

What falling *can't* remove is the difference in pull between neighbouring points: tides. Drop two balls 10 m apart from 400 km up and follow them for 600 s with full gravity:

- side by side: 10 → **7.4716 m** (they converge, both heading to Earth's centre)
- one above the other: 10 → **15.8616 m** (the lower one is pulled harder)

The linear tidal equation (geodesic deviation) integrated along the fall predicts 7.4716 and 15.8616. The tidal tensor's eigenvalues at 400 km: $(-1, -1, +2)\times GM/r^3$. **This is curvature**: the same object as the leftover rotation after a loop in [the holonomy post](/posts/2026-08-22-field-strength-is-a-commutator), the part that doesn't go away in any frame.

## 4. Why mass curves spacetime: the trace is the field equation

Add up the tidal eigenvalues (the trace): how fast a small ball of free-falling dust shrinks in volume.

- in vacuum, 400 km up: $-1 - 1 + 2 = 0$. Measured $-2\times10^{-17}$ s⁻², against eigenvalues of $1.3\times10^{-6}$.
- inside a uniform-density Earth ($\rho$ = 5514 kg/m³): $-4.6242\times10^{-6}$ s⁻², and $-4\pi G\rho = -4.6242\times10^{-6}$.

That one equation is the slow-speed limit of Einstein's field equation, $R_{00} = 4\pi G(\rho + 3p/c^2)$: **matter sets how fast a ball of falling dust shrinks** (Baez & Bunn 2005, who build all of general relativity from this sentence).

The honest "why": general relativity doesn't explain *why* energy curves spacetime. It gives two reasons the law has this form:

1. **Gravity is geometry because it is universal.** If everything falls the same way regardless of composition, the fall is a property of spacetime, not of the object. Tested: MICROSCOPE satellite (Touboul et al., PRL 2022), composition differences below $10^{-15}$. Established.
2. **The equation is forced.** Lovelock (1971): in 4 dimensions, the only local equation built from the metric, with up to second derivatives, that respects energy conservation is Einstein's (plus a cosmological constant). Established mathematics.

Given those two, there is no other choice. That is as far as "why" goes inside the theory.

## Where this stops working

- **Quantising it.** Every other force lives *on* spacetime; this one *is* spacetime. Quantising it means quantising the stage, and the perturbative theory produces new infinities at each order (Goroff & Sagnotti 1986, two loops). Open problem.
- **The proper-time maximum is local.** Over long enough times there can be several stationary paths (e.g. an orbit vs. going straight up and down); "maximum" means maximum among nearby paths.
- My setup uses the uniform-acceleration metric (Rindler). It has a clock gradient but no curvature, which is exactly why Section 3 needs the real Earth field.

*This is wrong if* maximising proper time with $g = 0$ leaves a bent path, or the vacuum tidal trace is non-zero beyond finite-difference error.
