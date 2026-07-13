---
title: "Kalman filters don't subtract noise — they weight belief"
date: 2026-04-21
tags: ["kalman-filter", "estimation", "noise", "intuition"]
status: growing
domain: signal
draft: false
attribution: "your confusion, sharpened into insight by ChatGPT"
sources:
  - kind: chatgpt
    date: 2026-04-21
    speaker: you
    role: spark
    quote: "I just don't see how Kalman filters filter noise or process noise. It seems like it's just added to the forward matrix."
  - kind: chatgpt
    date: 2026-04-21
    speaker: chatgpt
    role: crystallization
    quote: "Not \"subtracting noise,\" but **refusing to overreact to measurements that look more like noise than state change**."
---

I was stuck thinking a Kalman filter removes noise directly, as if process noise gets added to the forward matrix and cancelled somehow. The real point is that noise never gets subtracted at all — $Q$ and $R$ just tell the filter how much to trust the model versus the observation. Process noise inflates the predicted covariance, which raises the Kalman gain and makes the filter more willing to chase new data; measurement noise does the opposite. So 'filtering' is really refusing to overreact to a surprise that looks more like measurement noise than genuine state change. $F$ handles the deterministic mean evolution; $Q$ is added to covariance after that, not to $F$ itself.
