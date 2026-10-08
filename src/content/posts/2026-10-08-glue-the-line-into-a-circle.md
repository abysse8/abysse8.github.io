---
title: "Glue the line into a circle and the integral of e^(-x²) falls out"
date: 2026-10-08
blurb: "exp turns + into ×, and the inputs it can't tell apart (θ ~ θ+2π) are exactly what rolls the real line into a circle. That circle is the 2π in ∫e^{-x²} = √π, the same gluing turns the plane into a sphere, and integrating over circle × circle counts how many times two loops link."
tags: ["math", "topology", "integration", "numerics"]
hero: /posts/quotients.png
code: /posts/quotients.py
draft: true
---

The thread starts at an old note of mine: complex numbers complete calculus the way negative numbers complete arithmetic. The specific mechanism is one map.

## + becomes ×, and the line becomes a circle

$\exp$ turns addition into multiplication: $e^{a+b} = e^a e^b$. Feed it imaginary inputs and it lands on the unit circle, $\theta \mapsto e^{i\theta}$. It isn't one-to-one: $\theta$ and $\theta + 2\pi$ land on the same point. Declare those inputs equal, written $\theta \sim \theta + 2\pi$, and the real line *becomes* the circle: $\mathbb{R}/2\pi\mathbb{Z} \cong S^1$. The gluing is a theorem about the map, not a picture.

Check that could fail: $e^{i\cdot 1.1}$ and $e^{i(1.1+6\pi)}$ differ by $6\times10^{-16}$; $e^{i\cdot 1.1}$ and $e^{i\cdot 2.1}$ differ by $0.96$. If the code glued everything, the second number would be 0 too.

## The 2π in the Gaussian integral is that circle

$I = \int_{-\infty}^{\infty} e^{-x^2}\,dx$ has no antiderivative in closed form. Square it:

$$I^2 = \iint e^{-x^2} e^{-y^2}\,dx\,dy = \iint e^{-(x^2+y^2)}\,dx\,dy.$$

The second equality is the + ↔ × step. It makes the integrand depend on the radius only, so polar coordinates split it into a circle times a ray:

$$I^2 = \underbrace{\int_0^{2\pi} d\theta}_{\text{length of } \mathbb{R}/2\pi\mathbb{Z}} \int_0^\infty e^{-r^2} r\,dr = 2\pi\cdot\tfrac12 = \pi.$$

Falsifier: $e^{-|x|^3}$. Its product at $(1,0)$ and $(0.71, 0.71)$, the same radius, differs by $0.125$. No radial symmetry, so no circle factors out and no trick. The Gaussian is special *because* exp turns the sum of squares into a product.

A second appearance of gluing: the trapezoid rule on the whole line, step $h$, is wrong only by **aliasing**. Poisson summation says sampling every $h$ is the same as periodising, i.e. gluing $x \sim x + 2\pi/h$ on the frequency side, and predicts the error $2\sqrt\pi\, e^{-\pi^2/h^2}$. Measured vs predicted agree to 3 digits from $h = 1.5$ down to machine precision. Shift the grid by $h/3$ and the prediction says the error flips sign and halves ($\times\cos(2\pi/3)$): measured $-9.168\times10^{-5}$, predicted $-9.168\times10^{-5}$.

## Plane + one point = sphere

Stereographic projection sends the plane onto the sphere minus its north pole. Points far away crowd the pole: distance $\approx 2/|p|$ (measured 0.1990, 0.0200, 0.0020 at $|p| = 10, 100, 1000$). Add a single point $\infty$ and send it to the pole: $\mathbb{R}^2 \cup \{\infty\} \cong S^2$. The line version gives $\mathbb{R}\cup\{\infty\} \cong S^1$, a second, different route from line to circle.

## Knots: integrals over circle × circle

A closed curve in space is a map out of $S^1$, which is why the trefoil formula closes up ($|\gamma(0)-\gamma(2\pi)| = 10^{-15}$). Two closed curves give a map out of $S^1\times S^1$: the plane glued in *both* directions, a torus. Gauss (1833) wrote an integral over exactly that torus:

$$\mathrm{Lk} = \frac{1}{4\pi}\oint\!\!\oint \frac{(\mathbf r_1 - \mathbf r_2)\cdot(\mathbf r_1'\times\mathbf r_2')}{|\mathbf r_1-\mathbf r_2|^3}\,dt\,ds$$

A continuous computation that must return an integer: Hopf link → 1, separated circles → 0, the torus link $T(2,4)$ → 2. Because the domain is glued (periodic), the plain trapezoid rule converges *exponentially*: error $10^{-16}$ by 64 points per circle (Trefethen & Weideman, SIAM Review 2014, explain why).

## Where this stops working

- **Linking number 0 doesn't mean unlinked.** The Whitehead link has $\mathrm{Lk}=0$ and still can't be pulled apart. The integral is an invariant, not a complete one.
- **A single knot has no linking number with itself.** Whether the trefoil is knotted isn't decided by this integral. That needs a different invariant (the Alexander polynomial is the classical next one).

That second point is the knot question: what computation over the glued circle *does* detect a single knot?

*This is wrong if* a curve deformed without cutting changes its computed Lk by a non-integer amount, or the Gaussian trick works for a non-radial product.
