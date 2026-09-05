# Formal Mathematical Model & System Specification

This document provides the formal mathematical specification of the **Adaptive Hierarchical Automata Engine**, aligned with the Phase 1–9 implementation.

---

## 1. Core Automata Definitions

### 1.1 Deterministic Finite Automaton (DFA)
A Deterministic Finite Automaton $M_{DFA}$ is formally defined as a 5-tuple:
$$M_{DFA} = (Q, \Sigma, \delta, q_0, F)$$
where:
- $Q$ is a finite set of states.
- $\Sigma$ is a finite input alphabet (protocol message tokens).
- $\delta: Q \times \Sigma \rightarrow Q$ is the deterministic transition function.
- $q_0 \in Q$ is the initial state.
- $F \subseteq Q$ is the set of accepting (valid) states.

An input sequence $w = (\sigma_1, \sigma_2, \dots, \sigma_n) \in \Sigma^*$ is accepted by $M_{DFA}$ if there exists a sequence of states $(r_0, r_1, \dots, r_n)$ such that $r_0 = q_0$, $r_{i} = \delta(r_{i-1}, \sigma_i)$ for $i = 1, \dots, n$, and $r_n \in F$.

---

### 1.2 Mealy Machine (Stateful Transducer)
A Mealy Machine $M_{Mealy}$ extends the DFA to produce output symbols on state transitions:
$$M_{Mealy} = (Q, \Sigma, \Lambda, \delta, \lambda, q_0)$$
where:
- $Q, \Sigma, q_0$ are defined as above.
- $\Lambda$ is a finite output alphabet (e.g. protocol response actions / state flags).
- $\delta: Q \times \Sigma \rightarrow Q$ is the transition function.
- $\lambda: Q \times \Sigma \rightarrow \Lambda$ is the output function.

The transduction function $T: \Sigma^* \rightarrow \Lambda^*$ maps an input sequence $w = (\sigma_1, \dots, \sigma_n)$ to an output sequence $(\lambda(r_0, \sigma_1), \dots, \lambda(r_{n-1}, \sigma_n))$.

---

### 1.3 Pushdown Automaton (PDA)
A Deterministic Pushdown Automaton $M_{PDA}$ recognizes context-free structural depth (e.g. nested sessions / balanced message pairs):
$$M_{PDA} = (Q, \Sigma, \Gamma, \delta, q_0, z_0, F)$$
where:
- $\Gamma$ is a finite stack alphabet.
- $z_0 \in \Gamma$ is the initial stack symbol.
- $\delta: Q \times (\Sigma \cup \{\epsilon\}) \times \Gamma \rightarrow Q \times \Gamma^*$ is the transition function.

---

### 1.4 Context-Free Grammar (CFG)
A Context-Free Grammar $G$ is defined as a 4-tuple:
$$G = (V, \Sigma, R, S)$$
where:
- $V$ is a finite set of non-terminal variables.
- $\Sigma$ is a finite set of terminal symbols ($V \cap \Sigma = \emptyset$).
- $R \subseteq V \times (V \cup \Sigma)^*$ is a finite set of production rules.
- $S \in V$ is the start symbol.

---

## 2. Hierarchical Analysis Engine

The Hierarchical Analyzer evaluates input sequence $w$ across tiered automata models in order of computational complexity:

$$f_{hier}(w) = \begin{cases}
(\text{DFA}, \text{ACCEPT}) & \text{if } w \in L(M_{DFA}) \\
(\text{PDA}, \text{ACCEPT}) & \text{if } w \notin L(M_{DFA}) \land w \in L(M_{PDA}) \\
(\text{CFG}, \text{ACCEPT}) & \text{if } w \notin L(M_{PDA}) \land w \in L(G) \\
(\text{REJECT}, \text{DEVIATION}) & \text{otherwise}
\end{cases}$$

The fast-path DFA tier short-circuits standard protocol traffic in $O(|w|)$ time, avoiding expensive PDA push/pop stack operations or CFG parsing algorithms.

---

## 3. Adaptive Model Engine & Safeguards

### 3.1 Novelty Detection & Evidence Accumulation
When a sequence $w$ causes a deviation ($f_{hier}(w) = \text{REJECT}$), it is flagged as a candidate novel transition.

Let $e = (q_i, \sigma, q_j)$ be the unmodeled transition. The evidence accumulation score $E(e)$ over observation window $W$ is defined as:
$$E(e) = \sum_{k=1}^{|W|} I(e, w_k) \cdot \text{weight}(s_k)$$
where $I(e, w_k)$ indicates the presence of transition $e$ in session sequence $w_k$, and $\text{weight}(s_k)$ is a multi-session diversity weight.

---

### 3.2 Concept Drift Detection (Jensen-Shannon Divergence)
To verify that an observed novelty represents legitimate protocol evolution rather than an attack, the distribution of state transitions $P_{baseline}$ is compared with recent observation window distribution $P_{observed}$ using Jensen-Shannon Divergence:

$$D_{JS}(P_{baseline} \parallel P_{observed}) = \frac{1}{2} D_{KL}(P_{baseline} \parallel M) + \frac{1}{2} D_{KL}(P_{observed} \parallel M)$$
where $M = \frac{1}{2}(P_{baseline} + P_{observed})$ and $D_{KL}$ is the Kullback-Leibler divergence.

Adaptation is triggered if and only if $D_{JS} \le \tau_{drift}$, ensuring gradual, consistent protocol drift is accepted while anomalous high-divergence spikes are rejected.

---

### 3.3 Formal Model Validator
Before a candidate updated automaton $M_{cand} = (Q', \Sigma, \delta', q_0', F')$ can be promoted to active status, it must satisfy the Bounded Model Checking Safety Assertion $V(M_{cand})$:

$$V(M_{cand}) = \bigwedge_{w \in T_{known}} I(w \in L(M_{cand})) \land \bigwedge_{s \in S_{safety}} \text{CheckInvariant}(M_{cand}, s)$$

If $V(M_{cand}) = 1$, the candidate model is promoted to a new version $v_{k+1}$ in the immutable `ModelRegistry`; otherwise, the update is rejected and logged.

---

## 4. Safety & Immutability Properties

1. **Deterministic Execution**: Given state $q \in Q$ and input $\sigma \in \Sigma$, $|\delta(q, \sigma)| \le 1$.
2. **Atomic Version Lineage**: For every model version $v_k$, $\text{parent}(v_k) = v_{k-1}$, enabling rollback $R(v_k) \rightarrow v_{k-1}$.
3. **Formal Isolation**: The AI agentic layer is strictly read-only relative to automata models; it cannot directly mutate states or transition tables without passing through `FormalValidator`.
