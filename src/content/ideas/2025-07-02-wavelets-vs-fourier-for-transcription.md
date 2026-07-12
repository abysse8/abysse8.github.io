---
title: "Why transcription might be a wavelet, not a Fourier, process"
date: 2025-07-02
tags: [signal-processing, biology, learning-rules]
status: spark
draft: false
sources:
  - kind: claude
    date: 2025-07-02
    quote: "Is there a connection between wavelet analysis and the way DNA transcription seems both linear and well-normalized?"
---

Fourier assumes stationarity — a signal whose statistics don't move. DNA
transcription is the opposite: bursty, localized, scale-dependent. That's the
exact regime wavelets were built for. If the transcription machinery is reading a
signal that is "linear and well-normalized" only *locally*, then a multi-
resolution basis — coarse structure at the gene scale, fine structure at the
codon scale — is the honest model. The provocation: a learning algorithm derived
from this would update weights at multiple time-scales simultaneously, the way a
wavelet decomposes a signal, rather than at the single global scale that batched
backpropagation assumes.
