"""
Phase 4 Demonstration: Hierarchical Formal-Analysis Engine.

Demonstrates:
  1. DFA/Mealy Fast-Path resolution (Level 1) for standard protocol traces.
  2. Pushdown Automata (PDA) Escalation (Level 2) for matching nested container blocks.
  3. Context-Free Grammar (CFG) Escalation (Level 3) for recursive payload structure.
  4. Non-malicious unknown structural deviation handling (Level 4).
  5. Measurement of processing time, escalation rates, and unified classification metrics.
"""

from pathlib import Path
import time

from adaptive_automata.core import (
    State,
    PushdownAutomaton,
    StackOp,
    Grammar,
    Terminal,
    NonTerminal,
    CFGParser,
)
from adaptive_automata.protocol import create_toy_protocol_sut, TraceLoader
from adaptive_automata.learning import PassiveInferenceEngine, HybridActiveLearner
from adaptive_automata.models import ModelRegistry
from adaptive_automata.analysis import HierarchicalAnalyzer, AnalysisLevel, AnalysisStatus


def build_nested_container_pda() -> PushdownAutomaton[str, str]:
    """Build Pushdown Automaton for matching nested OPEN_BLOCK / CLOSE_BLOCK containers."""
    p_s0 = State("p0", is_initial=True)
    p_s1 = State("p1")
    p_s2 = State("p2", is_accepting=True)

    pda = PushdownAutomaton[str, str]("ContainerPDA", initial_stack_symbol="$")
    pda.add_state(p_s0)
    pda.add_state(p_s1)
    pda.add_state(p_s2)

    # Transition: p0 --['OPEN_BLOCK', top=$ / PUSH('B')]--> p1
    pda.add_transition(p_s0, "OPEN_BLOCK", "$", p_s1, op=StackOp.PUSH, push_symbols=["B"])
    # Transition: p1 --['OPEN_BLOCK', top=B / PUSH('B')]--> p1
    pda.add_transition(p_s1, "OPEN_BLOCK", "B", p_s1, op=StackOp.PUSH, push_symbols=["B"])
    # Transition: p1 --['DATA', top=B / NOP]--> p1
    pda.add_transition(p_s1, "DATA", "B", p_s1, op=StackOp.NOP)
    # Transition: p1 --['CLOSE_BLOCK', top=B / POP]--> p1
    pda.add_transition(p_s1, "CLOSE_BLOCK", "B", p_s1, op=StackOp.POP, pop_count=1)
    # Transition: p1 --['FIN', top=$ / NOP]--> p2
    pda.add_transition(p_s1, "FIN", "$", p_s2, op=StackOp.NOP)

    pda.validate()
    return pda


def build_recursive_payload_cfg() -> CFGParser:
    """Build CFG Parser for validating recursive grammar payload structures."""
    S = NonTerminal("S")
    A = NonTerminal("A")

    t_header = Terminal("HEADER")
    t_body = Terminal("BODY")

    g = Grammar(start_symbol=S)
    g.add_rule(S, [t_header, A, t_body])
    g.add_rule(A, [t_header, A, t_body])
    g.add_rule(A, [t_body])
    g.validate()

    return CFGParser(g)


def main() -> None:
    print("==========================================================================")
    print("  Adaptive Automata Engine - Phase 4 Hierarchical Analysis Demonstration")
    print("==========================================================================\n")

    # 1. Setup Fast-Path Model from Phase 3 Hybrid Engine
    data_dir = Path(__file__).parent / "data"
    v1_path = data_dir / "toy_protocol_v1.json"
    sessions = TraceLoader.load_from_file(str(v1_path))

    passive_engine = PassiveInferenceEngine()
    passive_model = passive_engine.infer_model(sessions, model_id="HierarchicalProto", version="v1.0.0-passive")

    sut = create_toy_protocol_sut()
    hybrid_learner = HybridActiveLearner[str, str]()
    fast_path_model = hybrid_learner.refine_model(passive_model, sut, new_version="v1.1.0-hybrid")

    registry = ModelRegistry()
    registry.register_model(fast_path_model)

    print(f"[*] Level 1 Fast-Path Model Loaded: '{fast_path_model.model_id}' ({fast_path_model.version})")
    print(f"[*] Level 1 Model States: {fast_path_model.num_states}, Transitions: {fast_path_model.num_transitions}\n")

    # 2. Setup Level 2 PDA and Level 3 CFG Parser
    pda = build_nested_container_pda()
    cfg_parser = build_recursive_payload_cfg()

    analyzer = HierarchicalAnalyzer(
        fast_path_model=fast_path_model,
        pda=pda,
        cfg_parser=cfg_parser,
    )

    # 3. Controlled Test Scenarios
    test_cases = [
        ("Scenario A (Standard Protocol Session)", ["SYN", "ACK", "AUTH", "DATA", "FIN"]),
        ("Scenario B (Nested Framing Containers)", ["OPEN_BLOCK", "OPEN_BLOCK", "DATA", "CLOSE_BLOCK", "CLOSE_BLOCK", "FIN"]),
        ("Scenario C (Recursive Grammar Structure)", ["HEADER", "HEADER", "BODY", "BODY", "BODY"]),
        ("Scenario D (Non-Malicious Unknown Deviation)", ["MALFORMED_SYMBOL", "BAD_TAG"]),
    ]

    print("=== Formal Model Hierarchical Escalation Execution ===\n")

    level_counts = {
        AnalysisLevel.DFA_MEALY: 0,
        AnalysisLevel.PDA: 0,
        AnalysisLevel.CFG: 0,
        AnalysisLevel.UNRESOLVED: 0,
    }
    status_counts = {status: 0 for status in AnalysisStatus}
    total_time_ms = 0.0

    for name, seq in test_cases:
        t0 = time.perf_counter()
        result = analyzer.analyze_sequence(seq)
        t_elapsed = (time.perf_counter() - t0) * 1000.0
        total_time_ms += t_elapsed

        level_counts[result.level_used] += 1
        status_counts[result.status] += 1

        print(f"[*] {name}:")
        print(f"    Input Sequence: {seq}")
        print(f"    [=>] Final Status: {result.status.value}")
        print(f"    [=>] Level Used:   {result.level_used.value}")
        print(f"    [=>] Reason:       {result.reason}")
        print(f"    [=>] Latency:      {t_elapsed:.3f} ms\n")

    # 4. Evaluation Metrics Summary
    print("=== Evaluation & Formal Model Escalation Metrics ===")
    total_inputs = len(test_cases)
    dfa_resolved = level_counts[AnalysisLevel.DFA_MEALY]
    pda_escalations = level_counts[AnalysisLevel.PDA]
    cfg_escalations = level_counts[AnalysisLevel.CFG] + level_counts[AnalysisLevel.UNRESOLVED]

    print(f"[+] Total Test Sequences Evaluated: {total_inputs}")
    print(f"[+] Fast-Path (DFA/Mealy) Resolved:  {dfa_resolved} ({dfa_resolved / total_inputs * 100:.1f}%)")
    print(f"[+] Level 2 (PDA) Escalations:       {pda_escalations} ({pda_escalations / total_inputs * 100:.1f}%)")
    print(f"[+] Level 3 (CFG) Escalations:       {cfg_escalations} ({cfg_escalations / total_inputs * 100:.1f}%)")
    print(f"[+] Total Processing Time:           {total_time_ms:.3f} ms (avg {total_time_ms / total_inputs:.3f} ms/sequence)\n")

    print("[*] Unified Classification Breakdown:")
    for status, cnt in status_counts.items():
        if cnt > 0:
            print(f"    - {status.value:<20}: {cnt}")

    print("\n[+] Phase 4 Hierarchical Formal-Analysis Engine executed successfully!")


if __name__ == "__main__":
    main()
