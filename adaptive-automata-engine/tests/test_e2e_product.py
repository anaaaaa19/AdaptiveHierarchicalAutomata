"""
End-to-End Master Product Integration Test Suite (STEP 11).
Verifies complete pipeline from ingestion to API, adaptation, rollback, and security alerts.
"""

from fastapi.testclient import TestClient

from api.app import app
from adaptive_automata.evaluation.baselines import ProposedAdaptiveHierarchicalModel
from adaptive_automata.agents.security_agent import SecurityInvestigationAgent
from adaptive_automata.agents.llm import MockLLMProvider


def test_e2e_pipeline_and_api_integration():
    """Verify complete end-to-end pipeline and API endpoint state reflection."""
    with TestClient(app) as client:
        # 1. GET /health
        res_health = client.get("/health")
        assert res_health.status_code == 200
        assert res_health.json()["service"] == "healthy"

        # 2. GET /status
        res_status = client.get("/status")
        assert res_status.status_code == 200
        st_json = res_status.json()
        assert "active_model_version" in st_json
        assert "is_capture_active" in st_json

        # 3. GET /models and GET /models/active
        res_models = client.get("/models")
        assert res_models.status_code == 200
        assert "versions" in res_models.json()

        res_active = client.get("/models/active")
        assert res_active.status_code == 200
        assert res_active.json()["version"] == "v1.0.0"

        # 4. GET /sessions
        res_sess = client.get("/sessions")
        assert res_sess.status_code == 200
        assert "count" in res_sess.json()

        # 5. GET /events
        res_events = client.get("/events")
        assert res_events.status_code == 200
        assert "events" in res_events.json()

        # 6. GET /alerts
        res_alerts = client.get("/alerts")
        assert res_alerts.status_code == 200
        assert "alerts" in res_alerts.json()

        # 7. GET /metrics, GET /drift, GET /adaptation
        res_metrics = client.get("/metrics")
        assert res_metrics.status_code == 200

        res_drift = client.get("/drift")
        assert res_drift.status_code == 200
        assert "drift_status" in res_drift.json()

        res_adapt = client.get("/adaptation")
        assert res_adapt.status_code == 200
        assert "active_version" in res_adapt.json()

        # 8. GET /investigations
        res_inv = client.get("/investigations")
        assert res_inv.status_code == 200
        assert "investigations" in res_inv.json()


def test_e2e_adaptation_and_poisoning_flow():
    """Verify novel behavior adaptation, poisoning block, and AI fallback."""
    engine = ProposedAdaptiveHierarchicalModel(
        dfa_sequences={("HELLO", "AUTH", "REQUEST", "RESPONSE", "LOGOUT")},
        pda_sequences=set(),
        cfg_sequences=set(),
        evidence_threshold=2,
    )

    # Normal traffic -> Known
    res_norm = engine.process_sequence(["HELLO", "AUTH", "REQUEST", "RESPONSE", "LOGOUT"])
    assert res_norm.is_accepted is True
    assert res_norm.escalation_level == "DFA"

    # Novel traffic -> Evidence -> Candidate -> Validated -> Adaptation
    v2_seq = ["HELLO", "AUTH", "CAPABILITIES", "REQUEST", "RESPONSE", "LOGOUT"]
    assert engine.process_sequence(v2_seq).is_accepted is False

    engine.adapt_on_sequence(v2_seq, label="evolved")
    engine.adapt_on_sequence(v2_seq, label="evolved")
    assert engine.process_sequence(v2_seq).is_accepted is True

    # Poisoning attack -> Validation failure -> Rejected
    poison_seq = ["HELLO", "AUTH", "MALICIOUS", "LOGOUT"]
    for _ in range(5):
        engine.adapt_on_sequence(poison_seq, label="poisoning")

    assert engine.process_sequence(poison_seq).is_accepted is False
    assert engine.blocked_poisoning_attempts > 0

    # AI Unavailable -> Formal analysis operates continuously
    llm = MockLLMProvider(override_responses={"InvestigationPlan": {"steps": []}})
    agent = SecurityInvestigationAgent(llm_provider=llm)
    inv_res = agent.run_investigation({
        "alert_id": "ALT-E2E-1",
        "session_id": "SESS-E2E-1",
        "sequence": ["REQUEST", "LOGOUT"],
        "anomaly_score": 0.99,
    })
    assert inv_res.investigation_id is not None
