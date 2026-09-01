"""
Phase 2 Demonstration: Active L* Learning of Mealy Machine Protocol SUT.

Demonstrates:
  1. Black-box Protocol SUT initialization.
  2. Active L* learning loop execution.
  3. Observation Table closedness and consistency maintenance.
  4. Hypothesis state transducer construction.
  5. Practical and exact equivalence oracle verification.
"""

from adaptive_automata.protocol import create_toy_protocol_sut
from adaptive_automata.learning import (
    LStarLearner,
    ExactMealyEquivalenceOracle,
    WMethodEquivalenceOracle,
    RandomSequenceEquivalenceOracle,
)


def main() -> None:
    print("==========================================================================")
    print("  Adaptive Automata Engine - Phase 2 L* Active Learning Demonstration")
    print("==========================================================================\n")

    # 1. Initialize Black-Box Toy Protocol SUT
    sut = create_toy_protocol_sut()
    print("[*] Target SUT: Toy Stateful Protocol (4 states, 5 input symbols)")
    print(f"[*] Input Alphabet Sigma: {sorted(list(sut.input_alphabet))}\n")

    # 2. Run L* Active Learning with Exact Equivalence Oracle
    print("=== [1] Active Learning with Exact Equivalence Oracle ===")
    exact_oracle = ExactMealyEquivalenceOracle[str, str]()
    learner = LStarLearner[str, str](equivalence_oracle=exact_oracle)
    result = learner.learn(sut)

    print(f"[+] Learning Converged: {result.converged}")
    print(f"[+] Learned States |Q|: {result.num_states}")
    print(f"[+] Learning Iterations: {result.learning_iterations}")
    print(f"[+] Membership Queries (O_MQ): {result.membership_queries}")
    print(f"[+] Total Symbols Queried: {result.total_symbols_queried}")
    print(f"[+] Equivalence Queries (O_EQ): {result.equivalence_queries}")
    print(f"[+] Counterexamples Processed: {result.counterexamples_found}")
    print(f"[+] Observation Table Size: {result.observation_table}\n")

    # 3. Print Learned Mealy Machine States and Transitions
    learned_machine = result.learned_mealy
    print(f"[*] Learned Mealy Machine State Graph ('{learned_machine.name}'):")
    for state in sorted(learned_machine.states, key=lambda s: s.name):
        init_str = " (Initial State)" if state.is_initial else ""
        print(f"    State '{state.name}'{init_str}:")
        for sym in sorted(list(learned_machine.input_alphabet)):
            learned_machine.reset()
            # Find transition out of state
            try:
                learned_machine._current_state = state
                tgt, out = learned_machine.step(sym)
                print(f"      --[{sym}]--> '{tgt.name}' / Output: '{out}'")
            except Exception as e:
                print(f"      --[{sym}]--> ERROR: {e}")
    print()

    # 4. Verify Transduction Equivalence on Sample Protocol Traces
    print("=== [2] Verifying Transduction Equivalence on Protocol Sequences ===")
    test_traces = [
        ("SYN", "ACK", "AUTH", "DATA", "FIN"),
        ("SYN", "ACK", "DATA"),
        ("ACK", "AUTH"),
        ("SYN", "SYN", "FIN"),
    ]

    for trace in test_traces:
        sut_out = sut.query(trace)
        hyp_out, _ = learned_machine.process_sequence(trace)
        match = (sut_out == tuple(hyp_out))
        print(f"  Input Trace: {list(trace)}")
        print(f"    SUT Output:     {list(sut_out)}")
        print(f"    Learned Model:  {hyp_out}")
        print(f"    [=>] Match: {match}\n")

    # 5. Run L* Active Learning with Bounded Practical Oracles
    print("=== [3] Active Learning with W-Method Equivalence Oracle ===")
    w_learner = LStarLearner[str, str](
        equivalence_oracle=WMethodEquivalenceOracle[str, str](max_depth=3)
    )
    w_result = w_learner.learn(sut)
    print(f"[+] W-Method Converged: {w_result.converged}, States: {w_result.num_states}, Queries: {w_result.membership_queries}\n")

    print("=== [4] Active Learning with Random Sequence Equivalence Oracle ===")
    rand_learner = LStarLearner[str, str](
        equivalence_oracle=RandomSequenceEquivalenceOracle[str, str](
            max_sequence_length=6, num_sequences=100, seed=42
        )
    )
    rand_result = rand_learner.learn(sut)
    print(f"[+] Random Sequence Converged: {rand_result.converged}, States: {rand_result.num_states}, Queries: {rand_result.membership_queries}\n")

    print("\n[+] Phase 2 Active Automata Learning framework executed successfully!")


if __name__ == "__main__":
    main()
