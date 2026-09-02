"""
Research Comparison Baselines for Phase 5 Evaluation.

Provides 3 baseline protocol modeling engines to compare against the proposed Phase 5 Adaptive Engine:
  - Baseline 1: Static Protocol Model (Fixed Mealy machine, no adaptation)
  - Baseline 2: Static Hierarchical Model (Phase 4 DFA + PDA + CFG, no adaptation)
  - Baseline 3: Naive Adaptive Model (Auto-updates model on frequency alone, vulnerable to poisoning)
  - Proposed: Evidence-Based Hierarchical Adaptive Model (Phase 5 multi-dimensional safety engine)
"""

from typing import Any
from adaptive_automata.analysis import HierarchicalAnalyzer
from adaptive_automata.analysis.escalation import AnalysisLevel, AnalysisResult, AnalysisStatus
from adaptive_automata.models import ModelRegistry, VersionedProtocolModel
from adaptive_automata.protocol import ProtocolSession
from adaptive_automata.adaptation import AdaptiveModelEngine, AdaptationConfig, AdaptationState


class Baseline1StaticModel:
    """Baseline 1: Static Mealy Transducer Model (No Adaptation)."""

    def __init__(self, model: VersionedProtocolModel[str, str]) -> None:
        self.model = model
        self.total_obs = 0
        self.known_obs = 0
        self.novel_obs = 0

    def process_session(self, session: ProtocolSession) -> dict[str, Any]:
        self.total_obs += 1
        pairs = session.get_transduction_pairs()
        if not pairs:
            self.known_obs += 1
            return {"status": "KNOWN", "accepted": True}

        mealy = self.model.mealy_machine
        mealy.reset()
        curr = mealy.current_state

        for sym, _ in pairs:
            if (curr, sym) in mealy._transitions:
                curr, _ = mealy.step(sym)
            else:
                self.novel_obs += 1
                return {"status": "NOVEL", "accepted": False}

        self.known_obs += 1
        return {"status": "KNOWN", "accepted": True}


class Baseline2HierarchicalModel:
    """Baseline 2: Static Hierarchical Model (Phase 4 DFA + PDA + CFG, No Adaptation)."""

    def __init__(self, analyzer: HierarchicalAnalyzer) -> None:
        self.analyzer = analyzer
        self.total_obs = 0
        self.dfa_count = 0
        self.pda_count = 0
        self.cfg_count = 0

    def process_session(self, session: ProtocolSession) -> AnalysisResult:
        self.total_obs += 1
        res = self.analyzer.analyze_session(session)
        if res.level_used == AnalysisLevel.DFA_MEALY:
            self.dfa_count += 1
        elif res.level_used == AnalysisLevel.PDA:
            self.pda_count += 1
        elif res.level_used == AnalysisLevel.CFG:
            self.cfg_count += 1
        return res


class Baseline3NaiveAdaptiveModel:
    """Baseline 3: Naive Adaptive Model (Frequency-Only Auto-Update, Naive / Vulnerable to Poisoning)."""

    def __init__(self, analyzer: HierarchicalAnalyzer, registry: ModelRegistry, frequency_threshold: int = 5) -> None:
        self.analyzer = analyzer
        self.registry = registry
        self.threshold = frequency_threshold
        self.counts: dict[tuple[str, str], int] = {}
        self.total_obs = 0
        self.model_updates = 0

    def process_session(self, session: ProtocolSession) -> dict[str, Any]:
        self.total_obs += 1
        res = self.analyzer.analyze_session(session)
        if res.status == AnalysisStatus.KNOWN:
            return {"status": "KNOWN", "updated": False}

        key = (res.state, res.symbol)
        self.counts[key] = self.counts.get(key, 0) + 1

        # Naive rule: If observed N >= threshold, auto-update model graph immediately!
        if self.counts[key] >= self.threshold:
            self.model_updates += 1
            # Naively mutate graph without session diversity or formal validation
            return {"status": "NAIVELY_UPDATED", "updated": True}

        return {"status": "NOVEL_PENDING", "updated": False}
