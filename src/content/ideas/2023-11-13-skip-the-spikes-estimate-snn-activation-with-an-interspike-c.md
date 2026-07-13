---
title: "Skip the spikes: estimate SNN activation with an interspike closeness score"
date: 2023-11-13
tags: ["spiking-neural-networks", "wavelets", "activation-estimation", "neuromorphic"]
status: growing
draft: false
attribution: "your hypothesis, your words"
sources:
  - kind: chatgpt
    date: 2023-11-13
    speaker: you
    role: spark
    quote: "instead we can just pass all the timesteps through with no thresholding (an \"all-pass\" neuron) and instead estimate the activation by some sort of \"closeness score\" that is a custom sized sliding window at each neuron, that gives a higher score for larger weights that are close together"
  - kind: chatgpt
    date: 2023-11-13
    speaker: you
    role: crystallization
    quote: "Eventually I want to do wavelet decomposition on these layers to get the small details and general trends of activation at each layer in space."
---

I want to avoid simulating the messy thresholding and reset dynamics of biologically plausible spiking neurons. Instead of stepping each timestep through the network, my hunch is I can pass all timesteps through an "all-pass" neuron with no thresholding, then estimate activation with a custom-sized sliding window "closeness score" that rewards large weights clustered close together. On top of that, wavelet decomposition on each layer should let me pull out both fine spatial detail and general activation trends. It's unresolved whether a closeness score can faithfully stand in for the network's true nonlinear/chaotic spike propagation.
