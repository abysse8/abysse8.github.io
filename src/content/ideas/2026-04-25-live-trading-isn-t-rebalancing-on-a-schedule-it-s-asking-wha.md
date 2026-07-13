---
title: "Live trading isn't rebalancing on a schedule — it's asking 'what should I hold t"
date: 2026-04-25
tags: ["algorithmic-trading", "portfolio-optimization", "system-design", "backtesting"]
status: mature
domain: ai
draft: false
attribution: "spark: your pushback · architecture and constraints sharpened with ChatGPT"
sources:
  - kind: chatgpt
    date: 2026-04-25
    speaker: you
    role: spark
    quote: "And I don't agree with the fact that we have a rebalance date. What, what is that? Because all of the stocks are just doing one, like uh on one date, they're deciding whether to buy or sell."
  - kind: chatgpt
    date: 2026-04-25
    speaker: chatgpt
    role: crystallization
    quote: "We should stop thinking in terms of:

```text
Buy signal / sell signal for each stock
```

and start thinking in terms of:

```text
Target portfolio today
```"
---

I realized the 30-day rebalance window in my strategy is a research artifact, not a trading logic — it comes from walk-forward validation, not from how live API trading should work. If I only look every 30 days, I can't exploit a small stock that starts moving on day 7. So I want to separate two systems: an honest research backtester and a live decision engine that recomputes a target portfolio daily and only trades the difference. The one correction I accepted is that 'make the most money possible' can't be the literal objective — it needs drawdown, volatility, concentration, and turnover constraints or the optimizer will just dump everything into the most explosive name and eventually blow up.
