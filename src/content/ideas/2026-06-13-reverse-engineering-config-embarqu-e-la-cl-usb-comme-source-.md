---
title: "Reverse-engineering config embarquée: la clé USB comme source de vérité"
date: 2026-06-13
tags: ["reverse-engineering", "embedded-config", "firmware", "diff-binaire"]
status: growing
draft: false
attribution: "spark: you (l'observation terrain) · reformulé et cadré méthodiquement par ChatGPT"
sources:
  - kind: chatgpt
    date: 2026-06-13
    speaker: you
    role: spark
    quote: "on a inséré une flash drive avec une config différente, on a essayé, et ça l'a réinitialisé, ça a changé l'erreur et on ne sait pas trop comment, parce qu'on ne sait pas où d'autres dans les fichiers cette config était configurée. Donc comment il a su ? C'est ça la grande question."
  - kind: chatgpt
    date: 2026-06-13
    speaker: chatgpt
    role: crystallization
    quote: "L'observation que tu as faite avec la clé USB est justement intéressante parce qu'elle suggère qu'il existe une **source de vérité** quelque part :

- soit dans la clé ;
- soit dans une mémoire interne ;
- soit dans un identifiant matériel ;
- soit dans un checksum/signature."
---

Quand on insère une clé USB avec une config différente dans une UC, son comportement change — mais on ne sait pas quelle donnée précise a provoqué le changement. Ma vraie question n'est pas de décoder le protocole USB ou d'accéder aux serveurs verrouillés du fabricant, c'est de comprendre le mécanisme par lequel l'UC décide de son comportement au démarrage. Mon hunch, c'est qu'il existe une 'source de vérité' quelque part — dans la clé, une mémoire interne, un identifiant matériel ou un checksum — et qu'on peut la localiser par diff binaire avant/après boot plutôt que par sniffing USB brut. Si on comprend ce mécanisme de chargement, on peut générer automatiquement des configs cohérentes à partir de l'étude véhicule et les valider avant déploiement. Reste ouvert: où la config est-elle réellement lue, et faut-il vraiment l'accès serveur, ou les supports déjà en notre possession suffisent-ils.
