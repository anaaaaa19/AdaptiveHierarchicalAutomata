"""
Behavioral Analyzer component.

Combines formal automata analysis evidence (Phase 4 AnalysisResult), model novelty (Phase 5 NoveltyResult),
evidence accumulation, concept drift, and multi-stage session context into a explainable SecurityAssessment.
"""

from typing import Any

from adaptive_automata.analysis.escalation import AnalysisLevel, AnalysisResult, AnalysisStatus
from adaptive_automata.adaptation.evidence import BehaviorEvidence
from adaptive_automata.adaptation.novelty import NoveltyResult, NoveltyStatus
from adaptive_automata.protocol.session import ProtocolSession
from .assessment import BehavioralClassification, ReasonCode, SecurityAssessment, SeverityLevel
from .config import SecurityConfig
from .context import SessionBehaviorContext
from .risk import SessionRiskAggregator


class BehavioralAnalyzer:
    """
    Evaluates formal analysis and session context to generate explainable SecurityAssessments.
    """

    def __init__(
        self,
        config: SecurityConfig | None = None,
        aggregator: SessionRiskAggregator | None = None,
    ) -> None:
        self.config = config or SecurityConfig()
        self.aggregator = aggregator or SessionRiskAggregator(self.config)

    def analyze_security(
        self,
        session: ProtocolSession,
        analysis_result: AnalysisResult,
        novelty_result: NoveltyResult,
        evidence: BehaviorEvidence | None = None,
        drift_score: float | None = None,
    ) -> SecurityAssessment:
        """
        Produce explainable SecurityAssessment for a protocol session.

        Returns:
            SecurityAssessment container with severity, classification, and reason codes.
        """
        session_id = session.session_id
        model_ver = analysis_result.model_version

        # Retrieve or initialize SessionBehaviorContext
        ctx = self.aggregator.get_or_create_context(session_id, model_ver)

        is_dev = analysis_result.status != AnalysisStatus.KNOWN
        ctx.record_step(
            symbol=analysis_result.symbol,
            target_state=analysis_result.state,
            is_deviation=is_dev,
            deviation_details={"reason": analysis_result.reason, "level": analysis_result.level_used.value},
            is_terminal=analysis_result.symbol in ("FIN", "LOGOUT", "CLOSE"),
        )

        reasons: list[ReasonCode] = []
        risk_score = 0.0
        w = self.config.risk_weights

        # 1. Known Baseline Behavior
        if analysis_result.status == AnalysisStatus.KNOWN:
            return SecurityAssessment(
                session_id=session_id,
                model_version=model_ver,
                analysis_status=analysis_result.status,
                novelty_status=novelty_result.status,
                structural_status="FULLY_VALID",
                behavioral_classification=BehavioralClassification.KNOWN,
                severity=SeverityLevel.BENIGN,
                risk_score=0.0,
                reason_codes=[],
                evidence_details={"sequence_length": len(ctx.symbols_history)},
            )

        # 2. Evaluate Formal & Behavioral Deviation Evidence
        if analysis_result.status == AnalysisStatus.STRUCTURAL_VIOLATION:
            reasons.append(ReasonCode.STRUCTURAL_VIOLATION)
            risk_score += w.get("structural_violation", 0.4)

        if analysis_result.status == AnalysisStatus.NOVEL_BUT_VALID:
            if analysis_result.level_used == AnalysisLevel.PDA:
                structural_desc = "VALIDATED_BY_PDA_NESTING"
            elif analysis_result.level_used == AnalysisLevel.CFG:
                structural_desc = "VALIDATED_BY_CFG_GRAMMAR"
            else:
                structural_desc = "NOVEL_STRUCTURE"
        else:
            reasons.append(ReasonCode.UNKNOWN_TRANSITION)
            risk_score += w.get("unknown_transition", 0.2)
            structural_desc = "INVALID_MODEL_GRAPH"

        # Check for unexpected nesting or CFG parse failure
        if analysis_result.level_used == AnalysisLevel.CFG and analysis_result.status != AnalysisStatus.KNOWN:
            if "unexpected token" in analysis_result.reason.lower():
                reasons.append(ReasonCode.UNEXPECTED_NESTING)
                risk_score += w.get("unexpected_nesting", 0.3)

        # Check evidence history for poisoning suspicion (Single-session spam attack!)
        if evidence:
            if evidence.observation_count >= 10 and evidence.unique_session_count == 1:
                reasons.append(ReasonCode.POISONING_SUSPECTED)
                risk_score += w.get("poisoning_suspected", 0.5)

        # Check Concept Drift
        if drift_score and drift_score >= self.config.risk_weights.get("drift_threshold", 0.2):
            reasons.append(ReasonCode.MODEL_DRIFT)
            risk_score += 0.15

        # Check Multi-Stage Session Aggregated Risk
        agg_risk, agg_factors = self.aggregator.compute_aggregated_session_risk(ctx)
        risk_score += agg_risk
        if agg_risk > 0.3:
            reasons.append(ReasonCode.MULTI_STAGE_DEVIATION)

        if ctx.deviations_count >= self.config.repetition_threshold:
            reasons.append(ReasonCode.SUSTAINED_NOVEL_BEHAVIOR)

        # Final Risk Score Normalization
        final_risk = round(min(1.0, risk_score), 3)

        # Classify Severity & Behavioral Tag
        if final_risk >= self.config.high_severity_threshold:
            severity = SeverityLevel.HIGH
            classification = BehavioralClassification.POTENTIAL_ATTACK
        elif final_risk >= self.config.medium_severity_threshold:
            severity = SeverityLevel.MEDIUM
            classification = BehavioralClassification.SUSPICIOUS
        elif final_risk >= self.config.low_severity_threshold:
            severity = SeverityLevel.LOW
            classification = BehavioralClassification.NOVEL if analysis_result.status == AnalysisStatus.NOVEL_BUT_VALID else BehavioralClassification.PROTOCOL_VIOLATION
        else:
            severity = SeverityLevel.BENIGN
            classification = BehavioralClassification.NOVEL if analysis_result.status == AnalysisStatus.NOVEL_BUT_VALID else BehavioralClassification.KNOWN

        return SecurityAssessment(
            session_id=session_id,
            model_version=model_ver,
            analysis_status=analysis_result.status,
            novelty_status=novelty_result.status,
            structural_status=structural_desc,
            behavioral_classification=classification,
            severity=severity,
            risk_score=final_risk,
            reason_codes=reasons,
            evidence_details={
                "deviations_in_session": ctx.deviations_count,
                "sequence_length": len(ctx.symbols_history),
                "aggregated_factors": agg_factors,
                "analysis_reason": analysis_result.reason,
            },
        )
