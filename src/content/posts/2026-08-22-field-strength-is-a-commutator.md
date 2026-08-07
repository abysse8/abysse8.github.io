---
title: "The field strength is a commutator — walk a loop and measure the leftover rotation"
date: 2026-08-22
blurb: "The electromagnetic field tensor looks like a commutator, and it isn't a coincidence: F = [D_μ, D_ν]. Carry a vector around a closed loop on a curved surface and it comes back rotated — by exactly the enclosed curvature (ratio 1.000). That leftover rotation IS the field strength."
tags: ["physics", "gauge-theory", "geometry", "electromagnetism"]
hero: /posts/holonomy.png
code: /posts/holonomy.py
draft: false
---

The electromagnetic field tensor $F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu$ is antisymmetric — it looks like a commutator. In non-Abelian gauge theory it stops merely looking like one and *becomes* one:

$$F_{\mu\nu} = [D_\mu, D_\nu],$$

the commutator of covariant derivatives. So "field strength" means: **how much the space fails to commute.** That's abstract until you make it a rotation you can measure by walking in a circle.

## Walk a loop, keep a vector pointed "the same way"

Take a vector and carry it around a closed loop, at every step keeping it as parallel to itself as the surface allows (parallel transport — no twisting, just following the surface). On a **flat** plane it comes back exactly as it left. On a **curved** surface it comes back **rotated** — and the rotation angle is precisely the curvature enclosed by the loop.

![Left: the rotation after one loop equals the enclosed area on a slope-1 line (curvature = 1); flat space gives zero. Right: the vector returns rotated.](/posts/holonomy.png)

I transported a vector around loops of increasing size on a unit sphere. The leftover rotation versus the enclosed area (left panel): a straight line of slope **1.000** — the sphere's Gaussian curvature. On a flat plane, zero, always. The rotation isn't approximately the curvature; it *is* the curvature, integrated over the patch you circled.

## Why that rotation is a commutator

Going around a little rectangular loop is: transport in direction $\mu$, then $\nu$, then back along $\mu$, then back along $\nu$. If transporting-then-untransporting in the two directions **commuted**, everything would cancel and the vector would return unchanged. The rotation you're left with is exactly the amount by which the two transports *fail to commute* — the commutator $[D_\mu, D_\nu]$. Flat space: transports commute, holonomy zero. Curved space: they don't, and the mismatch is the curvature. Same object, two names.

## The same structure is electromagnetism

Swap "rotate a vector" for "advance a quantum phase" and you get gauge theory unchanged. A charged particle carried around a loop picks up a phase $\exp\!\big(i\tfrac{e}{\hbar}\oint A\cdot dl\big) = \exp\!\big(i\tfrac{e}{\hbar}\Phi\big)$ — set by the enclosed magnetic flux $\Phi = \int F$. That's the **Aharonov–Bohm effect**: the particle's phase fails to close by exactly the flux threading the loop, even where the field itself is zero. The electromagnetic field is the curvature of the phase connection; $F$ is the leftover-per-loop, precisely as the geometric curvature was the rotation-per-loop.

## The one idea

Curvature, force, field strength — one object: **the failure of parallel transport to commute around a loop.** You can measure it as a rotation (geometry), a phase (electromagnetism), or a matrix (non-Abelian gauge theory), but it's always the same thing — what you can't undo by going around. That $F_{\mu\nu}$ *looks* like a commutator is not a resemblance. It is one.

## From scratch

numpy — parallel transport on a sphere by frame rotation, holonomy vs enclosed area, flat-space control. [The script](/posts/holonomy.py) reproduces the measured slope of 1.

