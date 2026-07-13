---
title: "Accurate LU factorization doesn't guarantee an accurate solution"
date: 2025-04-03
tags: ["numerical-stability", "lu-factorization", "pivoting", "conditioning"]
status: growing
draft: false
attribution: "spark: your question · sharpened with ChatGPT"
sources:
  - kind: chatgpt
    date: 2025-04-03
    speaker: you
    role: spark
    quote: "Now how would you explain the discrepancy between x and x bar which is on the order of e8"
  - kind: chatgpt
    date: 2025-04-03
    speaker: chatgpt
    role: crystallization
    quote: "This shows that **accuracy of the factorization does not guarantee accuracy of the solution**, particularly in poorly conditioned systems."
---

I noticed that after swapping rows of A, my LU factorization reconstructed the matrix almost perfectly ($A - LU \approx 0$), yet the computed solution x still differed from the true answer by about $10^8$. My takeaway is that a correct factorization tells you nothing about the conditioning of the actual solve. The real culprit was choosing a small pivot (1.0) when much larger entries like $10^8$ were present, which produced huge multipliers in L and amplified rounding error during forward/backward substitution. What's still open is exactly how much of this is intrinsic ill-conditioning of A versus the avoidable damage from skipping pivoting.
