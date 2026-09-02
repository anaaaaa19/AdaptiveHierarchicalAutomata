"""Unit tests for SessionRiskAggregator and SessionBehaviorContext."""

from adaptive_automata.security import SessionBehaviorContext, SessionRiskAggregator


def test_session_behavior_context_recording():
    ctx = SessionBehaviorContext(session_id="sess_context", model_version="v1.0.0")
    assert ctx.deviations_count == 0

    ctx.record_step("SYN", target_state="q1", is_deviation=False)
    ctx.record_step("BAD_SYM", target_state="q1", is_deviation=True, deviation_details={"reason": "Unknown"})

    assert len(ctx.symbols_history) == 2
    assert ctx.deviations_count == 1
    assert len(ctx.recent_deviations) == 1


def test_session_risk_aggregator_escalation():
    aggregator = SessionRiskAggregator()
    ctx = aggregator.get_or_create_context("sess_multi", "v1.0.0")

    # Record 4 deviations in the same session
    for i in range(4):
        ctx.record_step(f"BAD_{i}", is_deviation=True)

    risk_score, factors = aggregator.compute_aggregated_session_risk(ctx)
    assert risk_score >= 0.5
    assert len(factors) >= 2
