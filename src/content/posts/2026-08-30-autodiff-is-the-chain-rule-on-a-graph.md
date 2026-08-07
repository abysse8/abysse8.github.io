---
title: "Autodiff isn't symbolic and isn't finite differences — it's the chain rule on the graph your program already built"
date: 2026-08-30
blurb: "requires_grad isn't symbolic differentiation and isn't finite differences — it records your program's operations and applies the chain rule in reverse. Exact to machine precision, no step size, and a million-dimensional gradient in two passes instead of two million evaluations."
tags: ["math", "autodiff", "machine-learning", "numerics"]
hero: /posts/autodiff.png
code: /posts/autodiff.py
draft: false
---

For a long time I thought `requires_grad=True` did symbolic differentiation — that PyTorch built a formula for the derivative the way SymPy would. My own gradient code did something different: finite differences, chained by hand across composed functions. Both mental models are wrong, and the truth is a cleaner third thing.

## Three ways to get a derivative

**Symbolic** (SymPy): manipulate the formula into a formula for its derivative. Exact — but you need a closed form, and the expression *swells*: differentiate a deep composition and the symbolic result explodes into thousands of terms.

**Finite differences**: nudge the input and divide, $\frac{f(x+h)-f(x-h)}{2h}$. No formula needed — but it's approximate, and you're caught in a step-size trap (left panel). Make $h$ too big and the approximation is crude (truncation); too small and subtracting nearly-equal numbers destroys your digits (roundoff). The error bottoms out around $10^{-11}$ **and only at one magic $h$** you don't know in advance.

**Automatic differentiation**: neither of those. It carries each intermediate value *together with its derivative* through the actual operations your program runs, applying the chain rule to each elementary step (whose derivative is known exactly). No formula to swell, no step size to tune.

![Left: finite-difference error vs step size — a U-curve bottoming at 1e-11; autodiff is exact (flat at machine precision, no h). Right: cost of a full n-dimensional gradient — finite differences needs 2n evaluations, autodiff ~2.](/posts/autodiff.png)

I built a 20-line autodiff (dual numbers: a value paired with its derivative, with rules like $(uv)' = u'v + uv'$ wired into `*`). On a test function it returned the derivative with **exactly zero error** — the green line pinned to machine precision, no step size anywhere. The finite-difference curve, for comparison, never does better than $10^{-11}$.

## Why the reframing matters — the cost

Accuracy is the small win. The big one is the right panel. To get a full gradient in $n$ dimensions, finite differences must nudge each input separately: $2n$ evaluations. **Reverse-mode** autodiff records the computation once and walks the chain rule *backwards* through the graph, producing *all* $n$ partial derivatives in a fixed ~2 passes — independent of $n$.

At $n=10^6$ — a modest neural network — that's **2 passes versus two million evaluations.** This isn't a nicety; it's the reason deep learning exists. Backpropagation *is* reverse-mode autodiff, and without it, training anything large would cost a million forward passes per step.

## The realization

Once you see it as a graph, the confusion dissolves. When you build `f` out of `x`, `f` is *already a node in the graph* — you don't re-wrap it or re-declare it; the derivative flows through the operations that connected them. My hand-chained finite differences were doing conceptually the same thing — the chain rule across a composition — just approximately, and at $2n$ times the cost.

## The falsifier

If autodiff were finite differences, it would have a step-size error and a best-$h$. It has neither: zero error, no $h$. If it were symbolic, a deep program would blow up into an unmanageable formula. It doesn't — it stays numbers flowing through a graph. Both alternatives are ruled out by what the code actually does.

## From scratch

A dual-number autodiff in ~20 lines of numpy, plus the finite-difference sweep and the cost comparison. [The script](/posts/autodiff.py) reproduces both panels.
