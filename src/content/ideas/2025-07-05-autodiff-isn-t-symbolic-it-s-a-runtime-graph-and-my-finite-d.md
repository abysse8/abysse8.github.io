---
title: "Autodiff isn't symbolic — it's a runtime graph, and my finite-difference chain r"
date: 2025-07-05
tags: ["autodiff", "pytorch", "chain-rule", "finite-differences"]
status: growing
draft: false
attribution: "your confusion and your own finite-difference code · clarified by ChatGPT mapping it to your terms"
sources:
  - kind: chatgpt
    date: 2025-07-05
    speaker: you
    role: spark
    quote: "what does requires.grad actually do? Is it not some symbolic differentiation like I did? Im confused. Can you show the source code"
  - kind: chatgpt
    date: 2025-07-05
    speaker: chatgpt
    role: crystallization
    quote: "It is **not symbolic differentiation** — it's **runtime graph-based autodiff**."
---

I was confused about what `requires_grad=True` actually does, assuming it was symbolic differentiation like SymPy. My mental model came from my own code, where I compute directional derivatives via finite differences and chain them manually across composed functions. The key realization is that PyTorch's autodiff is neither symbolic nor finite-difference — it records operations into a dynamic graph as they run, then applies the chain rule in reverse on `.backward()`. So I don't need to re-wrap intermediate values like `f` as new tensors; once `f` is built from `x`, it's already part of the graph and gradients flow through automatically. My finite-difference composition is doing conceptually the same chaining, just approximately.
