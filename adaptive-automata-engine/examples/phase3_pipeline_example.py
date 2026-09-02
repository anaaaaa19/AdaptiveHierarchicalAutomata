"""
Phase 3 Demonstration: Protocol Trace Inference, Active/Passive Hybrid Workflow,
Model Versioning, and Protocol Evolution Experiment.

Demonstrates:
  1. Recorded JSON trace loading and session reconstruction.
  2. Passive protocol state machine inference from recorded traffic traces.
  3. Transition observation counting and Laplace-smoothed confidence scoring.
  4. Immutable model versioning in ModelRegistry.
  5. Active/Passive Hybrid refinement of unexplored state transitions via Phase 2 L*.
  6. Protocol Evolution experiment detecting legitimate version extensions.
"""

from pathlib import Path
from adaptive_automata.protocol import (
    TraceLoader,
    PreGroupedSessionReconstructor,
    JSONMessageTokenizer,
    create_toy_protocol_sut,
)
from adaptive_automata.learning import (
    PassiveInferenceEngine,
    HybridActiveLearner,
    ProtocolEvolutionAnalyzer,
)
from adaptive_automata.models import ModelRegistry


def main() -> None:
    print("==========================================================================")
    print("  Adaptive Automata Engine - Phase 3 Trace Inference & Hybrid Engine")
    print("==========================================================================\n")

    registry = ModelRegistry()

    # 1. Load Recorded Protocol Traces
    data_dir = Path(__file__).parent / "data"
    v1_path = data_dir / "toy_protocol_v1.json"
    v2_path = data_dir / "toy_protocol_v2.json"

    print(f"[*] Loading Phase 3 Baseline Protocol Traces: {v1_path.name}")
    reconstructor = PreGroupedSessionReconstructor()
    v1_sessions = reconstructor.reconstruct_sessions(v1_path.read_text(encoding="utf-8"))

    print(f"[+] Loaded {len(v1_sessions)} pre-grouped protocol sessions.\n")

    # 2. Passive Protocol Inference
    print("=== [1] Passive Protocol Inference ===")
    tokenizer = JSONMessageTokenizer(header_field="cmd")
    passive_engine = PassiveInferenceEngine()

    passive_model = passive_engine.infer_model(
        sessions=v1_sessions,
        tokenizer=tokenizer,
        model_id="ToyProtocolEngine",
        version="v1.0.0-passive",
    )
    registry.register_model(passive_model)

    print(f"[+] Model Registered: ID='{passive_model.model_id}', Version='{passive_model.version}'")
    print(f"[+] Source: {passive_model.source.value}")
    print(f"[+] Number of Traces Processed: {passive_model.metrics['num_traces']}")
    print(f"[+] Number of Unique Symbols: {passive_model.metrics['num_symbols']}")
    print(f"[+] Number of States |Q|: {passive_model.num_states}")
    print(f"[+] Number of Transitions |delta|: {passive_model.num_transitions}")
    print(f"[+] Unexplored Transitions (N=0): {passive_model.num_unexplored_transitions}")
    print(f"[+] Passive Inference Time: {passive_model.metrics['inference_time_ms']} ms\n")

    print("[*] Passive Transition Confidence & Observation Counts:")
    for (src, sym), meta in passive_model.transition_metadata.items():
        print(f"    ({src:<4}, {sym:<5}) -> {meta.target_state:<4} / Out: {meta.output_symbol:<16} | N={meta.observation_count:<2}, conf={meta.confidence_score:.3f}, status={meta.status.value}")
    print()

    # 3. Active/Passive Hybrid Workflow
    print("=== [2] Active/Passive Hybrid Learning Refinement ===")
    sut = create_toy_protocol_sut()
    hybrid_learner = HybridActiveLearner[str, str]()

    hybrid_model = hybrid_learner.refine_model(
        passive_model=passive_model,
        sut=sut,
        new_version="v1.1.0-hybrid",
    )
    registry.register_model(hybrid_model)

    print(f"[+] Refined Model Registered: ID='{hybrid_model.model_id}', Version='{hybrid_model.version}'")
    print(f"[+] Active Queries Executed: {hybrid_model.metrics['hybrid_active_queries']}")
    print(f"[+] Hybrid States |Q|: {hybrid_model.num_states}")
    print(f"[+] Hybrid Transitions |delta|: {hybrid_model.num_transitions}")
    print(f"[+] Unexplored Transitions remaining: {hybrid_model.num_unexplored_transitions}")
    print(f"[+] Hybrid Refinement Time: {hybrid_model.metrics['hybrid_inference_time_ms']} ms\n")

    # 4. Protocol Evolution Experiment
    print("=== [3] Protocol Evolution Experiment (v1 -> v2) ===")
    print(f"[*] Loading Protocol Version 2 Extension Traces: {v2_path.name}")
    v2_sessions = reconstructor.reconstruct_sessions(v2_path.read_text(encoding="utf-8"))

    evolution_analyzer = ProtocolEvolutionAnalyzer()
    evolved_model, evol_result = evolution_analyzer.analyze_evolution(
        baseline_model=hybrid_model,
        new_sessions=v2_sessions,
        tokenizer=tokenizer,
        new_version="v2.0.0-evolution",
    )
    registry.register_model(evolved_model)

    print(f"[+] Evolved Model Registered: ID='{evolved_model.model_id}', Version='{evolved_model.version}'")
    print(f"[+] Valid Extension Detected: {evol_result.is_valid_protocol_extension}")
    print(f"[+] New States Introduced: {evol_result.new_states_detected}")
    print(f"[+] New Transitions Added: {len(evol_result.new_valid_transitions)}")
    print(f"[+] Analysis Summary: {evol_result.description}\n")

    print("[*] Newly Discovered Protocol Extension Transitions:")
    for meta in evol_result.new_valid_transitions:
        print(f"    ({meta.source_state}, {meta.input_symbol}) -> {meta.target_state} / Out: {meta.output_symbol} | N={meta.observation_count}, status={meta.status.value}")
    print()

    # 5. Registry Version History Audit
    print("=== [4] Model Registry Version History Audit ===")
    registered_versions = registry.list_versions("ToyProtocolEngine")
    print(f"[+] Registered Versions for 'ToyProtocolEngine': {registered_versions}")
    print(f"[+] Latest Registered Version: '{registry.get_latest_model('ToyProtocolEngine').version}'")

    print("\n[+] Phase 3 Protocol Trace Inference Pipeline executed successfully!")


if __name__ == "__main__":
    main()
