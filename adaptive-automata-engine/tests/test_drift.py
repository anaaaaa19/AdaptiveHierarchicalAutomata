"""Unit tests for ConceptDriftDetector using Jensen-Shannon Divergence."""

from adaptive_automata.adaptation.drift import ConceptDriftDetector, DriftConfig


def test_drift_below_threshold():
    detector = ConceptDriftDetector(DriftConfig(threshold=0.2, window_size=20))
    baseline = ["SYN", "ACK", "AUTH", "DATA", "FIN"] * 10
    recent = ["SYN", "ACK", "AUTH", "DATA", "FIN"] * 4

    result = detector.detect_drift(recent, baseline)
    assert not result.detected
    assert result.js_divergence_score < 0.2


def test_drift_above_threshold():
    detector = ConceptDriftDetector(DriftConfig(threshold=0.2, window_size=20))
    baseline = ["SYN", "ACK", "AUTH", "DATA", "FIN"] * 10
    recent = ["RENEW_TOKEN", "CAPABILITIES", "RENEW_TOKEN"] * 10

    result = detector.detect_drift(recent, baseline)
    assert result.detected
    assert result.js_divergence_score >= 0.2
    assert len(result.affected_behaviors) > 0


def test_drift_empty_inputs():
    detector = ConceptDriftDetector()
    result = detector.detect_drift([], [])
    assert not result.detected
    assert result.js_divergence_score == 0.0
