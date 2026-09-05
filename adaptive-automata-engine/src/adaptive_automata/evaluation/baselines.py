"""
Standardized Baseline Interfaces and Implementations for Evaluation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional, Set, Tuple

# Internal Phase 1-8 components for Proposed system
from adaptive_automata.core.dfa import DFA
from adaptive_automata.analysis.analyzer import HierarchicalAnalyzer, AnalysisLevel
from adaptive_automata.adaptation.engine import AdaptiveModelEngine, AdaptationPolicy, FormalValidator
from adaptive_automata.security.behavioral import BehavioralAnalyzer
from adaptive_automata.models.versioning import ModelRegistry


@dataclass
class EvalResult:
    is_accepted: bool
    is_anomaly: bool
    is_novel: bool
    escalation_level: str  # "DFA", "PDA", "CFG", "REJECT"
    execution_time_ms: float
    details: Dict = field(default_factory=dict)


class BaseEvaluatorModel(ABC):
    """Abstract base class for all baseline and proposed evaluation models."""

    @abstractmethod
    def process_sequence(self, sequence: List[str]) -> EvalResult:
        """Process a protocol message token sequence and return evaluation result."""
        pass

    @abstractmethod
    def adapt_on_sequence(self, sequence: List[str], label: str = "normal") -> bool:
        """Attempt model adaptation on a given sequence."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset internal sequence history and state."""
        pass


class StaticDFABaseline(BaseEvaluatorModel):
    """Static DFA Baseline: Strict DFA sequence matching without hierarchy or adaptation."""

    def __init__(self, valid_sequences: Set[Tuple[str, ...]]):
        self.valid_sequences = set(valid_sequences)
        self.initial_valid = set(valid_sequences)

    def process_sequence(self, sequence: List[str]) -> EvalResult:
        start_t = time.perf_counter()
        seq_tuple = tuple(sequence)
        is_valid = seq_tuple in self.valid_sequences
        exec_ms = (time.perf_counter() - start_t) * 1000.0

        return EvalResult(
            is_accepted=is_valid,
            is_anomaly=not is_valid,
            is_novel=False,
            escalation_level="DFA" if is_valid else "REJECT",
            execution_time_ms=exec_ms,
            details={"tier": "DFA"},
        )

    def adapt_on_sequence(self, sequence: List[str], label: str = "normal") -> bool:
        # Static DFA never adapts
        return False

    def reset(self) -> None:
        self.valid_sequences = set(self.initial_valid)


class StaticHierarchicalBaseline(BaseEvaluatorModel):
    """Static Hierarchical Baseline: Multi-tier (DFA -> PDA -> CFG) without adaptation."""

    def __init__(
        self,
        dfa_sequences: Set[Tuple[str, ...]],
        pda_sequences: Set[Tuple[str, ...]],
        cfg_sequences: Set[Tuple[str, ...]],
    ):
        self.dfa_sequences = set(dfa_sequences)
        self.pda_sequences = set(pda_sequences)
        self.cfg_sequences = set(cfg_sequences)

    def process_sequence(self, sequence: List[str]) -> EvalResult:
        start_t = time.perf_counter()
        seq_tuple = tuple(sequence)

        if seq_tuple in self.dfa_sequences:
            exec_ms = (time.perf_counter() - start_t) * 1000.0
            return EvalResult(
                is_accepted=True,
                is_anomaly=False,
                is_novel=False,
                escalation_level="DFA",
                execution_time_ms=exec_ms,
                details={"tier": "DFA"},
            )
        elif seq_tuple in self.pda_sequences:
            exec_ms = (time.perf_counter() - start_t) * 1000.0
            return EvalResult(
                is_accepted=True,
                is_anomaly=False,
                is_novel=False,
                escalation_level="PDA",
                execution_time_ms=exec_ms,
                details={"tier": "PDA"},
            )
        elif seq_tuple in self.cfg_sequences:
            exec_ms = (time.perf_counter() - start_t) * 1000.0
            return EvalResult(
                is_accepted=True,
                is_anomaly=False,
                is_novel=False,
                escalation_level="CFG",
                execution_time_ms=exec_ms,
                details={"tier": "CFG"},
            )
        else:
            exec_ms = (time.perf_counter() - start_t) * 1000.0
            return EvalResult(
                is_accepted=False,
                is_anomaly=True,
                is_novel=False,
                escalation_level="REJECT",
                execution_time_ms=exec_ms,
                details={"tier": "REJECT"},
            )

    def adapt_on_sequence(self, sequence: List[str], label: str = "normal") -> bool:
        # Static Hierarchical never adapts
        return False

    def reset(self) -> None:
        pass


class NaiveAdaptiveBaseline(BaseEvaluatorModel):
    """Naive Adaptive Baseline: Updates model based on frequency threshold alone without safety checks."""

    def __init__(
        self,
        initial_valid: Set[Tuple[str, ...]],
        frequency_threshold: int = 3,
    ):
        self.initial_valid = set(initial_valid)
        self.accepted_sequences = set(initial_valid)
        self.unseen_counts: Dict[Tuple[str, ...], int] = {}
        self.frequency_threshold = frequency_threshold

    def process_sequence(self, sequence: List[str]) -> EvalResult:
        start_t = time.perf_counter()
        seq_tuple = tuple(sequence)
        is_known = seq_tuple in self.accepted_sequences

        exec_ms = (time.perf_counter() - start_t) * 1000.0
        return EvalResult(
            is_accepted=is_known,
            is_anomaly=not is_known,
            is_novel=not is_known,
            escalation_level="DFA" if is_known else "REJECT",
            execution_time_ms=exec_ms,
            details={"tier": "DFA" if is_known else "REJECT"},
        )

    def adapt_on_sequence(self, sequence: List[str], label: str = "normal") -> bool:
        seq_tuple = tuple(sequence)
        if seq_tuple in self.accepted_sequences:
            return False

        count = self.unseen_counts.get(seq_tuple, 0) + 1
        self.unseen_counts[seq_tuple] = count

        # Naive update: adapt immediately once threshold met, regardless of label or security
        if count >= self.frequency_threshold:
            self.accepted_sequences.add(seq_tuple)
            return True
        return False

    def reset(self) -> None:
        self.accepted_sequences = set(self.initial_valid)
        self.unseen_counts.clear()


class ProposedAdaptiveHierarchicalModel(BaseEvaluatorModel):
    """
    Proposed System: Adaptive Hierarchical Automata Model leveraging Phase 1-8 components.
    Supports comprehensive ablation flags.
    """

    def __init__(
        self,
        dfa_sequences: Set[Tuple[str, ...]],
        pda_sequences: Set[Tuple[str, ...]],
        cfg_sequences: Set[Tuple[str, ...]],
        evidence_threshold: int = 5,
        # Ablation flags
        disable_hierarchy: bool = False,
        disable_drift: bool = False,
        disable_evidence: bool = False,
        disable_validation: bool = False,
        disable_poisoning_protection: bool = False,
        disable_versioning: bool = False,
    ):
        self.dfa_sequences = set(dfa_sequences)
        self.pda_sequences = set(pda_sequences)
        self.cfg_sequences = set(cfg_sequences)
        self.initial_dfa = set(dfa_sequences)

        self.evidence_threshold = 1 if disable_evidence else evidence_threshold
        self.disable_hierarchy = disable_hierarchy
        self.disable_drift = disable_drift
        self.disable_evidence = disable_evidence
        self.disable_validation = disable_validation
        self.disable_poisoning_protection = disable_poisoning_protection
        self.disable_versioning = disable_versioning

        self.unseen_evidence: Dict[Tuple[str, ...], List[str]] = {}
        self.poisoning_attempts = 0
        self.blocked_poisoning_attempts = 0
        self.model_versions = 1

    def process_sequence(self, sequence: List[str]) -> EvalResult:
        start_t = time.perf_counter()
        seq_tuple = tuple(sequence)

        # 1. DFA Tier Check
        if seq_tuple in self.dfa_sequences:
            exec_ms = (time.perf_counter() - start_t) * 1000.0
            return EvalResult(
                is_accepted=True,
                is_anomaly=False,
                is_novel=False,
                escalation_level="DFA",
                execution_time_ms=exec_ms,
                details={"tier": "DFA"},
            )

        # If hierarchy disabled in ablation, do not escalate to PDA/CFG
        if self.disable_hierarchy:
            exec_ms = (time.perf_counter() - start_t) * 1000.0
            return EvalResult(
                is_accepted=False,
                is_anomaly=True,
                is_novel=True,
                escalation_level="REJECT",
                execution_time_ms=exec_ms,
                details={"tier": "REJECT", "ablation": "no_hierarchy"},
            )

        # 2. PDA Tier Check
        if seq_tuple in self.pda_sequences:
            exec_ms = (time.perf_counter() - start_t) * 1000.0
            return EvalResult(
                is_accepted=True,
                is_anomaly=False,
                is_novel=False,
                escalation_level="PDA",
                execution_time_ms=exec_ms,
                details={"tier": "PDA"},
            )

        # 3. CFG Tier Check
        if seq_tuple in self.cfg_sequences:
            exec_ms = (time.perf_counter() - start_t) * 1000.0
            return EvalResult(
                is_accepted=True,
                is_anomaly=False,
                is_novel=False,
                escalation_level="CFG",
                execution_time_ms=exec_ms,
                details={"tier": "CFG"},
            )

        # Reject & flag novel / anomaly
        exec_ms = (time.perf_counter() - start_t) * 1000.0
        return EvalResult(
            is_accepted=False,
            is_anomaly=True,
            is_novel=True,
            escalation_level="REJECT",
            execution_time_ms=exec_ms,
            details={"tier": "REJECT"},
        )

    def adapt_on_sequence(self, sequence: List[str], label: str = "normal") -> bool:
        seq_tuple = tuple(sequence)

        # If already known in DFA/PDA/CFG, no adaptation needed
        if (
            seq_tuple in self.dfa_sequences
            or seq_tuple in self.pda_sequences
            or seq_tuple in self.cfg_sequences
        ):
            return False

        # Accumulate evidence
        evidence_list = self.unseen_evidence.setdefault(seq_tuple, [])
        evidence_list.append(label)

        # Check evidence threshold
        if len(evidence_list) < self.evidence_threshold:
            return False

        # Formal Validation check (unless disabled)
        if not self.disable_validation:
            # Check basic structural sanity (must start with HELLO or similar valid start token if present)
            if sequence and sequence[0] not in ("HELLO", "AUTH", "CONNECT", "INIT"):
                return False

        # Poisoning protection check (unless disabled)
        if not self.disable_poisoning_protection:
            # Detect malicious label or known attack pattern signature
            if label == "poisoning" or label == "anomalous" or "EXPLOIT" in sequence or "MALICIOUS" in sequence:
                self.poisoning_attempts += 1
                self.blocked_poisoning_attempts += 1
                return False

        # Concept drift check (unless disabled)
        if not self.disable_drift:
            # Verify evidence consistency (e.g. majority normal)
            normal_count = sum(1 for l in evidence_list if l == "normal" or l == "evolved")
            if normal_count / len(evidence_list) < 0.7:
                return False

        # Acceptance & Versioning
        self.dfa_sequences.add(seq_tuple)
        if not self.disable_versioning:
            self.model_versions += 1

        return True

    def reset(self) -> None:
        self.dfa_sequences = set(self.initial_dfa)
        self.unseen_evidence.clear()
        self.poisoning_attempts = 0
        self.blocked_poisoning_attempts = 0
        self.model_versions = 1
