"""
Hierarchical Formal-Analysis Engine.

Coordinates multi-tiered protocol evaluation:
  1. DFA/Mealy Fast Path (Level 1)
  2. Pushdown Automata (PDA) Nested Context (Level 2)
  3. Context-Free Grammar (CFG) Parser (Level 3)
"""

from typing import Sequence

from adaptive_automata.core.cfg import CFGParser
from adaptive_automata.core.mealy import InvalidMealyStateError
from adaptive_automata.core.pda import PushdownAutomaton, InvalidPDAStateError
from adaptive_automata.learning.confidence import ConfidenceLevel
from adaptive_automata.models.versioning import VersionedProtocolModel
from adaptive_automata.protocol.session import ProtocolSession
from adaptive_automata.protocol.tokenizer import BaseMessageTokenizer, HeaderCommandTokenizer
from .escalation import AnalysisLevel, AnalysisResult, AnalysisStatus, EscalationController
from .event import DeviationEvent


class HierarchicalAnalyzer:
    """
    Top-level Hierarchical Formal Analysis Engine for protocol behavior.

    Enforces the principle: 'Use the least expressive formal model capable of explaining
    the observed behavior, and escalate only when the simpler model fails.'
    """

    def __init__(
        self,
        fast_path_model: VersionedProtocolModel[str, str],
        pda: PushdownAutomaton[str, str] | None = None,
        cfg_parser: CFGParser | None = None,
        escalation_controller: EscalationController | None = None,
    ) -> None:
        self.fast_path_model = fast_path_model
        self.pda = pda
        self.cfg_parser = cfg_parser
        self.escalation = escalation_controller or EscalationController()

    def analyze_sequence(self, sequence: Sequence[str], session_id: str = "sess_analysis") -> AnalysisResult:
        """
        Evaluate an input symbol sequence through the formal model hierarchy.

        Returns:
            Unified AnalysisResult containing status, level_used, and metadata.
        """
        if not sequence:
            return AnalysisResult(
                status=AnalysisStatus.KNOWN,
                level_used=AnalysisLevel.DFA_MEALY,
                reason="Empty sequence accepted by default.",
                state="q0",
                symbol="",
                confidence_score=1.0,
                model_version=self.fast_path_model.version,
            )

        mealy = self.fast_path_model.mealy_machine
        mealy.reset()
        curr_state = mealy.current_state

        deviation: DeviationEvent | None = None

        # Level 1: Fast-Path Mealy Transducer Analysis
        for pos, sym in enumerate(sequence):
            st_name = curr_state.name if curr_state else "UNKNOWN"
            meta_key = (st_name, str(sym))
            meta = self.fast_path_model.transition_metadata.get(meta_key)

            # Check if transition is defined and valid
            if (curr_state, sym) in mealy._transitions:
                # Check confidence status
                if meta and meta.status == ConfidenceLevel.UNKNOWN:
                    deviation = DeviationEvent(
                        session_id=session_id,
                        current_state=st_name,
                        input_symbol=str(sym),
                        position=pos,
                        reason=f"Fast-path transition status is UNKNOWN (N=0).",
                        model_version=self.fast_path_model.version,
                        trace_snippet=tuple(sequence[: pos + 1]),
                    )
                    break

                try:
                    curr_state, _ = mealy.step(sym)
                except InvalidMealyStateError as e:
                    deviation = DeviationEvent(
                        session_id=session_id,
                        current_state=st_name,
                        input_symbol=str(sym),
                        position=pos,
                        reason=f"Invalid Mealy transition: {e}",
                        model_version=self.fast_path_model.version,
                        trace_snippet=tuple(sequence[: pos + 1]),
                    )
                    break
            else:
                deviation = DeviationEvent(
                    session_id=session_id,
                    current_state=st_name,
                    input_symbol=str(sym),
                    position=pos,
                    reason=f"Undefined Mealy transition from state '{st_name}' on symbol '{sym}'.",
                    model_version=self.fast_path_model.version,
                    trace_snippet=tuple(sequence[: pos + 1]),
                )
                break

        # Level 1 Success
        if deviation is None and curr_state is not None:
            return AnalysisResult(
                status=AnalysisStatus.KNOWN,
                level_used=AnalysisLevel.DFA_MEALY,
                reason="Sequence fully recognized by Level 1 DFA/Mealy fast path.",
                state=curr_state.name,
                symbol=str(sequence[-1]),
                confidence_score=1.0,
                model_version=self.fast_path_model.version,
            )

        assert deviation is not None

        # Level 2: Escalation to Pushdown Automaton (PDA)
        pda_failed = True
        if self.escalation.should_escalate_to_pda(deviation, sequence) and self.pda is not None:
            try:
                is_accepted, pda_state, stack_snap, _ = self.pda.process_sequence(sequence)
                if is_accepted:
                    return AnalysisResult(
                        status=AnalysisStatus.NOVEL_BUT_VALID,
                        level_used=AnalysisLevel.PDA,
                        reason="Validated by Level 2 Pushdown Automaton (matching nested framing/context).",
                        state=pda_state.name,
                        symbol=str(sequence[-1]),
                        confidence_score=0.9,
                        model_version=self.fast_path_model.version,
                        details={"stack_snapshot": stack_snap},
                    )
            except InvalidPDAStateError:
                pda_failed = True

        # Level 3: Escalation to Context-Free Grammar (CFG) Parser
        if self.escalation.should_escalate_to_cfg(deviation, sequence, pda_failed) and self.cfg_parser is not None:
            parse_res = self.cfg_parser.parse(sequence)
            if parse_res.is_valid:
                return AnalysisResult(
                    status=AnalysisStatus.NOVEL_BUT_VALID,
                    level_used=AnalysisLevel.CFG,
                    reason=f"Validated by Level 3 CFG Parser: {parse_res.reason}",
                    state=deviation.current_state,
                    symbol=str(sequence[-1]),
                    confidence_score=0.8,
                    model_version=self.fast_path_model.version,
                    details={"cfg_reason": parse_res.reason},
                )
            else:
                return AnalysisResult(
                    status=AnalysisStatus.STRUCTURAL_VIOLATION,
                    level_used=AnalysisLevel.CFG,
                    reason=f"CFG parse structural violation: {parse_res.reason}",
                    state=deviation.current_state,
                    symbol=deviation.input_symbol,
                    confidence_score=0.0,
                    model_version=self.fast_path_model.version,
                    details={"error_position": parse_res.error_position},
                )

        # Level 4: Unresolved Novel/Unknown Deviation
        return AnalysisResult(
            status=AnalysisStatus.UNKNOWN,
            level_used=AnalysisLevel.UNRESOLVED,
            reason=f"Unresolved protocol deviation: {deviation.reason}",
            state=deviation.current_state,
            symbol=deviation.input_symbol,
            confidence_score=0.0,
            model_version=self.fast_path_model.version,
            details={"deviation_event": deviation},
        )

    def analyze_session(
        self,
        session: ProtocolSession,
        tokenizer: BaseMessageTokenizer | None = None,
    ) -> AnalysisResult:
        """
        Tokenize a ProtocolSession and evaluate it through the hierarchical analyzer.
        """
        tok = tokenizer or HeaderCommandTokenizer()
        pairs = tok.tokenize_session(session)
        input_sequence = [inp for inp, _ in pairs]
        return self.analyze_sequence(input_sequence, session_id=session.session_id)
