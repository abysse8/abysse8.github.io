---
title: "A photon is one rung on the energy ladder of one mode of the field"
date: 2026-10-12
blurb: "Count the standing waves in a box, give each energy in steps of hf, and σ (Stefan-Boltzmann) comes out of h, c, k to 3e-11. Einstein's 1909 formula splits light's fluctuations into a particle term and a wave term; counting gives g2 = 1.99 for thermal light, 1.00 for a laser."
tags: ["physics", "quantum", "light", "statistics"]
hero: /posts/photons.png
code: /posts/photons.py
draft: false
---

"Photon" is usually explained as "a particle of light", which predicts things light doesn't do. The working definition is narrower and checkable.

## Step 1: light in a box is a set of independent oscillators

Put light in a closed metal box. The field can only oscillate in standing-wave patterns that fit: a whole number of half-wavelengths along each side, like the allowed notes of a guitar string. Each pattern is a **mode**. Each mode, mathematically, is one harmonic oscillator (a mass on a spring) with its own frequency $f$.

How many modes below frequency $f$? Brute force: count integer triples $(n_x, n_y, n_z)$ with $|n| \le 2Lf/c$, times 2 polarisations. Formula: $N = 8\pi V f^3/3c^3$.

| radius in mode space | counted / formula | (1 − ratio) × radius |
|---|---|---|
| 10 | 0.783 | 2.170 |
| 100 | 0.977 | 2.258 |
| 400 | 0.994 | 2.253 |

The ratio goes to 1, and the shortfall is the walls: Weyl's law predicts (1 − ratio) × radius → 9/4 = 2.250. Measured 2.25.

## Step 2: give each oscillator energy, two ways

**Continuous** (classical): any energy allowed. In thermal equilibrium every mode averages $kT$. There are $\propto f^3$ modes and they grow without bound, so total energy diverges. Measured energy density in a 5772 K cavity (the Sun's surface temperature) as I raise the frequency cutoff: 25, 198, 1586, 12 690 J/m³. No answer.

**Stepped** (Planck 1900): the oscillator's energy is $0, hf, 2hf, \dots$ only. Summing the Boltzmann weights directly gives an average of $hf/(e^{hf/kT}-1)$ (matched to 6 digits). High-frequency modes can't afford even one step, so they hold almost nothing: at $10^{15}$ Hz the average is 0.002 kT. Same cutoff sweep: 0.813, 0.840, 0.840, 0.840 J/m³. Converged.

From $h, c, k$ alone, the radiated power constant: $\sigma = 5.670374\times10^{-8}$ W m⁻² K⁻⁴, CODATA $5.670374419\times10^{-8}$, relative difference $3\times10^{-11}$. Shrink the step to $h/10$ and it becomes $5\times10^{-5}$; the answer depends on the step being exactly $h$. Spectrum peak at $hf/kT = 2.8214$ (Wien's law).

**So: a photon is one step up one mode's ladder.** "Three photons at 500 THz" means some mode near 500 THz is on rung 3. Nothing in this definition says "small ball at a position".

## Step 3: Einstein 1909, light fluctuates like both

How much does the number of photons $n$ in one thermal mode jitter? Summing the distribution:

$$\mathrm{Var}(n) = \bar n + \bar n^2.$$

Einstein got this from thermodynamics ($\mathrm{Var}(E) = kT^2\, d\langle E\rangle/dT$) and read it term by term. Independent particles give $\mathrm{Var} = \bar n$ (shot noise). Interfering random waves give $\mathrm{Var} = \bar n^2$. Light has both, and the script checks all three numbers agree at five temperatures. The particle share $\bar n / \mathrm{Var}$: 0.05 at $hf/kT = 0.05$ (radio: wave-like), 0.99 at $hf/kT = 5$ (visible light from a lamp: particle-like).

## Step 4: count photons and you can tell the source

Hanbury Brown & Twiss (1956) measured $g_2 = \langle n(n-1)\rangle/\bar n^2$, which tells you whether photons arrive in bunches. Simulated with 200 000 windows of mean 4 photons:

- thermal light: $g_2 = 1.993$, 95% CI [1.982, 2.005] (theory 2: bunched)
- laser light: $g_2 = 1.0003$, 95% CI [0.999, 1.002] (theory 1: random, Poisson)

Same average intensity, different statistics. The photon picture has to carry the state of the mode, not just its energy.

Scale: one 633 nm (red) photon is 1.96 eV; a 1 mW red laser pointer emits $3.2\times10^{15}$ per second.

## Where this stops working

- **A photon has no clean position.** The mode picture defines photons by frequency and box shape. There is no position operator for a photon in the usual sense (Newton & Wigner 1949). "Where is the photon" is a question about the detector that clicks.
- **The box is a choice.** Different boxes, different modes, different "photons". The count is basis-dependent; the field is not.
- **Carver Mead's alternative** (*Collective Electrodynamics*, 2000) treats a photon as an energy transfer between two resonating atoms, coupled through the four-potential. It reproduces the same numbers in the cases he treats. Evidence tier: an interpretation, not a different prediction I know of. The mainstream account is the field-mode one above (Loudon 2000).
- My mode count uses the scalar box rule ($n_i \ge 1$) times two polarisations. Real EM boundary conditions allow one index to be zero for some polarisations; that changes the wall correction, not the $f^3$ term.

*This is wrong if* σ computed from $h, c, k$ misses CODATA by more than integration error, or a thermal source shows $g_2 = 1$.
