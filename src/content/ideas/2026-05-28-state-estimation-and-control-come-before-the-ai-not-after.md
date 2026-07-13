---
title: "State estimation and control come before the AI, not after"
date: 2026-05-28
tags: ["robotics", "state-estimation", "drones", "control-systems"]
status: growing
draft: false
attribution: "your question · ChatGPT's structured synthesis"
sources:
  - kind: chatgpt
    date: 2026-05-28
    speaker: you
    role: spark
    quote: "Quels sont les différents algorithmes de navigation qui doivent être pris en compte et que je dois apprendre pour gérer une plateforme comme ça ?"
  - kind: chatgpt
    date: 2026-05-28
    speaker: chatgpt
    role: crystallization
    quote: "Beaucoup de gens sautent directement vers l’IA et ROS sans comprendre pourquoi leur drone dérive ou oscille."
---

When people try to build autonomous drones, they rush toward AI and ROS and then wonder why their drone drifts and oscillates. My real starting point should be state estimation (Kalman/EKF, sensor fusion) and control (PID), because those are the layers that make flight actually stable. The intelligent learning order is: control math (PID, coordinate frames, quaternions) → Kalman/EKF → MAVLink/PX4 → visual odometry/SLAM → path planning → high-level autonomy. My signal-processing and distributed-systems background maps cleanly onto Kalman filtering, noise, and telemetry, so this plays to my strengths. Open question is how far up the stack (SLAM, MPC) I actually need to go for my use case.
