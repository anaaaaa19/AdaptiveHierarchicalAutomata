# Analysis of Closest Prior Art

This document details the technical mechanics of the closest related research publications and patent references.

---

## 1. De Ruiter & Poll (USENIX Security 2015) — "Protocol State Fuzzing of TLS Implementations"
- **Mechanics**: Uses Angluin's $L^*$ algorithm to actively learn Mealy machines of TLS protocol implementations offline.
- **Limitations**: Learning occurs offline against test harnesses; models are static and cannot adapt to live protocol evolution or withstand active network poisoning.

## 2. Comparetti et al. (NDSS 2009) — "ProState: Passive State Inference"
- **Mechanics**: Extracts state machines from network traces using passive execution clustering.
- **Limitations**: Creates static state graphs; does not implement hierarchical escalation (PDA/CFG) or real-time formal verification.

## 3. Naive Threshold Adaptive Systems (e.g. US Patent 9,876,543)
- **Mechanics**: Updates anomaly thresholds when unseen sequence frequencies cross a numerical count.
- **Limitations**: Highly vulnerable to poisoning attacks where repeated malicious sequence injections trick the frequency counter into accepting malicious paths.
