---
title: "Un adaptateur universel qui traduit des protocoles d'affichage voyageur hétérogè"
date: 2026-05-20
tags: ["reverse-engineering", "rs485", "protocol-classification", "embedded"]
status: mature
domain: embedded
draft: false
attribution: "spark: you (observation terrain + vision projet) · structuré et articulé par ChatGPT"
revisits: [2026-05-13, 2026-05-13, 2026-05-13, 2026-05-14, 2026-05-15, 2026-05-19, 2026-05-27]
sources:
  - kind: chatgpt
    date: 2026-05-20
    speaker: you
    role: spark
    quote: "Really highlight the fact that they’re independent models that we don’t even think the [display vendor] uses RS 485 differential to the display it seems to be more independent because it has activity on the bus when the controller is off."
  - kind: chatgpt
    date: 2026-05-20
    speaker: chatgpt
    role: crystallization
    quote: "L’objectif n’est pas simplement de copier des bytes.

L’objectif est de reconstruire le sens logique des commandes."
---

Mon projet a basculé : ce n'est plus un simple sniffer RS485, mais une plateforme capable de comprendre plusieurs protocoles constructeurs propriétaires et de les traduire vers un modèle logique intermédiaire commun. Le déclic vient d'une anomalie : j'observe de l'activité sur le bus même quand le contrôleur semble éteint, ce qui casse l'hypothèse maître-esclave passif et suggère une architecture semi-indépendante dans le panneau. Le vrai verrou n'est plus l'acquisition du signal mais la classification fonctionnelle des trames — distinguer polling, payload, boot, synchronisation, réponses — surtout en contexte multi-panneaux qu'on ne maîtrise pas faute de matériel. À terme, j'aimerais que l'adaptateur soit piloté via WiFi pour devenir un point d'entrée moderne vers ces systèmes anciens.
