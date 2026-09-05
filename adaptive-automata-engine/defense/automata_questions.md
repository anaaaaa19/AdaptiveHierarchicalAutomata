# Research Defense: Automata & Formal Learning Q&A

### Q1: How does the system implement $L^*$ active learning?
**A**: `LStarMealyLearner` constructs an observation table $(S, E, T)$ querying a System Under Test (SUT) with membership queries. It resolves unclosed or inconsistent table states by extending prefixes or suffixes, and uses equivalence oracles ($W$-method, random walks) to find counterexamples.

### Q2: What formal safety properties does `FormalValidator` enforce?
**A**: `FormalValidator` ensures candidate models maintain valid initial and accepting states, preserve existing valid trace paths (zero regression), and do not introduce non-deterministic transitions.
