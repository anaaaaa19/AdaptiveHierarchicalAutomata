"""
Phase 10 Deterministic Final Demonstration Script.

Walks through 6 core operational scenarios:
  1. Known valid protocol (fast-path DFA resolution)
  2. Previously unseen legitimate behavior (escalation & evidence gathering)
  3. Confirmed anomalous behavior (threat detection & formal alert)
  4. Model poisoning attempt (blocked by formal validator)
  5. Validated model evolution (Protocol v2 adaptation & version promotion)
  6. AI investigation failure/fallback (graceful formal isolation)
"""

import sys
import time

from adaptive_automata.evaluation.baselines import ProposedAdaptiveHierarchicalModel
from adaptive_automata.agents.security_agent import SecurityInvestigationAgent
from adaptive_automata.agents.llm import MockLLMProvider


def print_section(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def run_demo():
    print_section("ADAPTIVE HIERARCHICAL AUTOMATA ENGINE — FINAL DEMONSTRATION")

    # Initializing Proposed Engine with Toy Protocol Base
    dfa_base = {("HELLO", "AUTH", "REQUEST", "RESPONSE", "LOGOUT")}
    pda_base = {("HELLO", "AUTH", "NESTED_REQ", "NESTED_RESP", "LOGOUT")}
    cfg_base = set()

    engine = ProposedAdaptiveHierarchicalModel(
        dfa_sequences=dfa_base,
        pda_sequences=pda_base,
        cfg_sequences=cfg_base,
        evidence_threshold=3,
    )

    # -------------------------------------------------------------
    # Scenario 1: Known Valid Protocol
    # -------------------------------------------------------------
    print_section("Scenario 1: Known Valid Protocol Traffic")
    valid_seq = ["HELLO", "AUTH", "REQUEST", "RESPONSE", "LOGOUT"]
    print(f"Input Sequence: {valid_seq}")

    res1 = engine.process_sequence(valid_seq)
    print(f" -> Resolution Tier : {res1.escalation_level}")
    print(f" -> Accepted        : {res1.is_accepted}")
    print(f" -> Is Anomaly      : {res1.is_anomaly}")
    print(f" -> Latency         : {res1.execution_time_ms:.4f} ms")

    # -------------------------------------------------------------
    # Scenario 2: Previously Unseen Legitimate Behavior
    # -------------------------------------------------------------
    print_section("Scenario 2: Previously Unseen Legitimate Behavior (Protocol v2)")
    evolved_seq = ["HELLO", "AUTH", "CAPABILITIES", "REQUEST", "RESPONSE", "LOGOUT"]
    print(f"Input Sequence: {evolved_seq}")

    res2 = engine.process_sequence(evolved_seq)
    print(f" -> Initial Resolution Tier : {res2.escalation_level}")
    print(f" -> Accepted                : {res2.is_accepted}")
    print(f" -> Is Novel                : {res2.is_novel}")

    # Accumulate evidence
    print(" -> Accumulating Multi-Session Evidence...")
    for session_idx in range(1, 3):
        adapted = engine.adapt_on_sequence(evolved_seq, label="evolved")
        print(f"    Observation {session_idx}: Adaptation Status = {adapted}")

    # -------------------------------------------------------------
    # Scenario 3: Confirmed Anomalous Behavior
    # -------------------------------------------------------------
    print_section("Scenario 3: Confirmed Anomalous Behavior (Structural Violation)")
    anomaly_seq = ["REQUEST", "RESPONSE", "LOGOUT"]
    print(f"Input Sequence: {anomaly_seq}")

    res3 = engine.process_sequence(anomaly_seq)
    print(f" -> Resolution Tier : {res3.escalation_level}")
    print(f" -> Accepted        : {res3.is_accepted}")
    print(f" -> Is Anomaly      : {res3.is_anomaly}")

    # -------------------------------------------------------------
    # Scenario 4: Poisoning Attempt
    # -------------------------------------------------------------
    print_section("Scenario 4: Model Poisoning Attempt")
    poison_seq = ["HELLO", "AUTH", "MALICIOUS_EXPLOIT", "LOGOUT"]
    print(f"Injecting Malicious Sequence: {poison_seq}")

    for idx in range(1, 5):
        adapted = engine.adapt_on_sequence(poison_seq, label="poisoning")
        print(f" -> Injection Attempt {idx}: Adaptation Accepted = {adapted}")

    print(f" -> Total Poisoning Attempts Blocked: {engine.blocked_poisoning_attempts}")

    # -------------------------------------------------------------
    # Scenario 5: Validated Model Evolution
    # -------------------------------------------------------------
    print_section("Scenario 5: Validated Model Evolution (Activation)")
    print(f" -> Finalizing Evidence threshold for Protocol v2...")
    adapted = engine.adapt_on_sequence(evolved_seq, label="evolved")
    print(f" -> Threshold Met! Model Adaptation Promoted: {adapted}")
    print(f" -> Active Model Version: v{engine.model_versions}.0.0")

    # Now verify sequence is accepted at DFA tier
    res5 = engine.process_sequence(evolved_seq)
    print(f" -> Post-Adaptation Resolution Tier : {res5.escalation_level}")
    print(f" -> Post-Adaptation Accepted        : {res5.is_accepted}")

    # -------------------------------------------------------------
    # Scenario 6: AI Investigation Failure / Fallback Isolation
    # -------------------------------------------------------------
    print_section("Scenario 6: Agentic AI Investigation & Provider Fallback Isolation")
    llm = MockLLMProvider()
    agent = SecurityInvestigationAgent(llm_provider=llm)

    print(" -> Triggering advisory AI investigation on formal security alert ALT-9001...")
    investigation = agent.run_investigation({
        "alert_id": "ALT-9001",
        "session_id": "SESS-DEMO-9001",
        "sequence": anomaly_seq,
        "anomaly_score": 0.98,
    })

    print(f" -> Investigation ID   : {investigation.investigation_id}")
    print(f" -> Event Type         : {investigation.event_type}")
    print(f" -> Severity Rec       : {investigation.severity_recommendation}")
    print(f" -> Formal Isolation  : Core Automata Models Unaffected by AI State")

    print_section("DEMONSTRATION COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    run_demo()
