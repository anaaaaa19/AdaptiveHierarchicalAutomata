"""
Passive Protocol Inference Engine.

Infers a Mealy Machine transducer from observed protocol trace sessions using Prefix Tree
Acceptor (PTA) construction, state merging, and transition observation frequency tracking.
"""

from collections import defaultdict
import time
from typing import Generic, Sequence, TypeVar

from adaptive_automata.core.mealy import MealyMachine
from adaptive_automata.core.state import State
from adaptive_automata.models.versioning import ModelSource, VersionedProtocolModel
from adaptive_automata.protocol.session import ProtocolSession
from adaptive_automata.protocol.tokenizer import BaseMessageTokenizer, HeaderCommandTokenizer
from .confidence import ConfidenceCalculator, ConfidenceLevel, TransitionMetadata

SymbolT = TypeVar("SymbolT")
OutputT = TypeVar("OutputT")


class PassiveInferenceEngine:
    """
    Infers state machine protocol models passively from recorded session traces.
    """

    def __init__(self, confidence_calculator: ConfidenceCalculator | None = None) -> None:
        self.confidence_calc = confidence_calculator or ConfidenceCalculator()

    def infer_model(
        self,
        sessions: Sequence[ProtocolSession],
        tokenizer: BaseMessageTokenizer | None = None,
        model_id: str = "PassiveProtocolModel",
        version: str = "v1.0.0",
    ) -> VersionedProtocolModel[str, str]:
        """
        Passively infer a VersionedProtocolModel from a collection of ProtocolSessions.

        Args:
            sessions: List of recorded ProtocolSessions.
            tokenizer: Message tokenizer for extracting (input, output) symbols.
            model_id: Identifier string for model.
            version: Model version tag.

        Returns:
            VersionedProtocolModel containing inferred MealyMachine and confidence metrics.
        """
        start_time = time.perf_counter()
        tok = tokenizer or HeaderCommandTokenizer()

        # Step 1: Extract all session transduction sequences
        session_traces: list[list[tuple[str, str]]] = []
        alphabet_inputs: set[str] = set()
        alphabet_outputs: set[str] = set()

        for sess in sessions:
            pairs = tok.tokenize_session(sess)
            if pairs:
                session_traces.append(pairs)
                for inp, out in pairs:
                    alphabet_inputs.add(inp)
                    alphabet_outputs.add(out)

        # Step 2: Build Prefix Tree Acceptor (PTA)
        # Node structure: id -> dict of (inp_sym) -> (target_node_id, output_sym)
        pta_nodes: list[str] = ["q0"]
        pta_transitions: dict[tuple[str, str], tuple[str, str]] = {}
        transition_counts: dict[tuple[str, str, str, str], int] = defaultdict(int)

        node_counter = 1

        for trace in session_traces:
            curr_node = "q0"
            for inp, out in trace:
                key = (curr_node, inp)
                if key in pta_transitions:
                    next_node, existing_out = pta_transitions[key]
                    transition_counts[(curr_node, inp, next_node, out)] += 1
                    curr_node = next_node
                else:
                    new_node = f"q{node_counter}"
                    node_counter += 1
                    pta_nodes.append(new_node)
                    pta_transitions[key] = (new_node, out)
                    transition_counts[(curr_node, inp, new_node, out)] += 1
                    curr_node = new_node

        # Step 3: State Merging (merge equivalent future states)
        # Partition PTA nodes by outgoing signature: dict mapping tuple of (inp -> out) to state group
        node_out_sig: dict[str, tuple[tuple[str, str], ...]] = {}
        for n in pta_nodes:
            sig = []
            for inp in sorted(alphabet_inputs):
                if (n, inp) in pta_transitions:
                    tgt, out = pta_transitions[(n, inp)]
                    sig.append((inp, out))
            node_out_sig[n] = tuple(sig)

        # Group nodes with identical signatures
        sig_to_merged: dict[tuple[tuple[str, str], ...], str] = {}
        node_to_merged: dict[str, str] = {}
        merged_counter = 0

        for n in pta_nodes:
            sig = node_out_sig[n]
            if sig not in sig_to_merged:
                if n == "q0":
                    m_label = "q0"
                else:
                    m_label = f"q{merged_counter + (1 if 'q0' in sig_to_merged.values() else 0)}"
                    merged_counter += 1
                sig_to_merged[sig] = m_label
            node_to_merged[n] = sig_to_merged[sig]

        # Construct merged Mealy machine
        merged_states: dict[str, State] = {}
        mealy = MealyMachine[str, str](name=f"{model_id}_{version}")

        # Add states
        for m_label in sorted(set(node_to_merged.values())):
            st = State(m_label, is_initial=(m_label == "q0"))
            merged_states[m_label] = st
            mealy.add_state(st)

        # Add transitions and aggregate counts
        merged_counts: dict[tuple[str, str, str, str], int] = defaultdict(int)
        for (src, inp, tgt, out), count in transition_counts.items():
            m_src = node_to_merged[src]
            m_tgt = node_to_merged[tgt]
            merged_counts[(m_src, inp, m_tgt, out)] += count

        added_transitions: set[tuple[str, str]] = set()
        for (m_src, inp, m_tgt, out), count in merged_counts.items():
            t_key = (m_src, inp)
            if t_key not in added_transitions:
                mealy.add_transition(merged_states[m_src], inp, merged_states[m_tgt], out)
                added_transitions.add(t_key)

        mealy.validate()

        # Step 4: Compute Transition Metadata & Confidence
        transition_metadata: dict[tuple[str, str], TransitionMetadata] = {}

        # Compute total observations per state
        state_total_obs: dict[str, int] = defaultdict(int)
        for (m_src, inp, m_tgt, out), count in merged_counts.items():
            state_total_obs[m_src] += count

        alphabet_size = len(alphabet_inputs)

        for st in mealy.states:
            m_src = st.name
            tot_obs = state_total_obs[m_src]

            for inp in sorted(alphabet_inputs):
                key = (m_src, inp)
                # Find matching transition in mealy
                if (st, inp) in mealy._transitions:
                    m_tgt_st, out = mealy._transitions[(st, inp)]
                    m_tgt = m_tgt_st.name
                    obs_cnt = 0
                    for (s_k, i_k, t_k, o_k), c in merged_counts.items():
                        if s_k == m_src and i_k == inp and t_k == m_tgt:
                            obs_cnt += c

                    score, status = self.confidence_calc.compute_confidence(obs_cnt, tot_obs, alphabet_size)
                    transition_metadata[key] = TransitionMetadata(
                        source_state=m_src,
                        input_symbol=inp,
                        target_state=m_tgt,
                        output_symbol=out,
                        observation_count=obs_cnt,
                        confidence_score=score,
                        status=status,
                    )
                else:
                    # Unexplored transition
                    score, status = self.confidence_calc.compute_confidence(0, tot_obs, alphabet_size)
                    transition_metadata[key] = TransitionMetadata(
                        source_state=m_src,
                        input_symbol=inp,
                        target_state="UNKNOWN",
                        output_symbol="NONE",
                        observation_count=0,
                        confidence_score=score,
                        status=ConfidenceLevel.UNKNOWN,
                    )

        inference_time = (time.perf_counter() - start_time) * 1000.0

        unexplored_cnt = sum(1 for m in transition_metadata.values() if m.observation_count == 0)

        metrics = {
            "num_traces": len(sessions),
            "num_symbols": alphabet_size,
            "num_states": len(mealy.states),
            "num_transitions": len(mealy._transitions),
            "unexplored_transitions": unexplored_cnt,
            "inference_time_ms": round(inference_time, 2),
        }

        return VersionedProtocolModel[str, str](
            model_id=model_id,
            version=version,
            source=ModelSource.PASSIVE_INFERENCE,
            mealy_machine=mealy,
            transition_metadata=transition_metadata,
            metrics=metrics,
        )
