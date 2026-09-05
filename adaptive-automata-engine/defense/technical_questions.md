# Research Defense: Technical Implementation Q&A

### Q1: How does the evidence accumulation mechanism prevent single-session attacks?
**A**: `EvidenceStore` enforces a multi-session diversity requirement (`unique_session_count >= tau`). A single attacker flooding millions of malicious packets within one session cannot trigger model adaptation.

### Q2: How does Jensen-Shannon Divergence ($D_{JS}$) detect concept drift?
**A**: $D_{JS}$ compares state transition probability distributions between a baseline window and recent observation windows. Gradual protocol drift yields low divergence ($D_{JS} \le 0.15$), triggering adaptation review, whereas abrupt attack bursts yield high divergence ($D_{JS} > 0.40$), causing candidate rejection.
