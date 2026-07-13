---
title: "Document profiles, not hardcoded fields: a YAML control layer for enterprise doc"
date: 2026-05-26
tags: ["document-generation", "enterprise-software", "architecture", "yaml-config"]
status: mature
domain: ai
draft: false
attribution: "spark: you · architecture sharpened with ChatGPT"
revisits: [2026-05-22, 2026-05-28, 2026-05-29, 2026-06-03]
sources:
  - kind: chatgpt
    date: 2026-05-26
    speaker: you
    role: spark
    quote: "Je pense que ca vaut le coup de generaliser ce concept de human rules qui decrivent le formatting."
  - kind: chatgpt
    date: 2026-05-26
    speaker: chatgpt
    role: crystallization
    quote: "The app does not need to know what an étude véhicule is. It only needs to know what a document profile says."
---

I want to generalize my étude véhicule doc generator into a configurable enterprise document maker, since the same field-service exports also drive facturation and other workflows. My key insight is that the 'human rules' describing formatting shouldn't be hardcoded per document type — they should live in a declarative layer. The clean architecture separates a generic document engine (load template, apply context, render DOCX/PDF, report missing fields) from métier-specific 'document profiles' (a profile.yaml naming the template, fields, display labels, and which values need human review). React only displays rules and collects decisions; it must not become the rule engine. Open question is discipline: build one vertical slice first while naming things generically, rather than trying to build a universal document platform up front.
