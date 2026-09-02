"""Unit tests for ModelUpdater."""

import pytest
from adaptive_automata.core import State, MealyMachine
from adaptive_automata.models import ModelSource, VersionedProtocolModel, ModelRegistry
from adaptive_automata.adaptation.candidate import CandidateModel
from adaptive_automata.adaptation.evidence import BehaviorEvidence
from adaptive_automata.adaptation.lifecycle import AdaptationState
from adaptive_automata.adaptation.updater import ModelUpdater


def create_baseline_model() -> VersionedProtocolModel[str, str]:
    s0 = State("q0", is_initial=True)
    mealy = MealyMachine[str, str]("TestUpdater")
    mealy.add_state(s0)
    return VersionedProtocolModel[str, str](
        model_id="TestUpdater",
        version="v1.0.0",
        source=ModelSource.ACTIVE_HYBRID,
        mealy_machine=mealy,
    )


def test_model_updater_success():
    registry = ModelRegistry()
    baseline = create_baseline_model()
    registry.register_model(baseline)

    updater = ModelUpdater(registry)
    ev = BehaviorEvidence("q0:AUTH", "q0", "AUTH", observation_count=5)
    cand = CandidateModel(
        candidate_id="cand_1",
        parent_version="v1.0.0",
        proposed_transitions=[("q0", "AUTH", "q1", "GRANT")],
        supporting_evidence=ev,
        lifecycle_state=AdaptationState.VALIDATED,
    )

    new_model = updater.apply_update(cand, baseline, "v2.0.0-adapted")
    assert new_model.version == "v2.0.0-adapted"
    assert registry.get_model("TestUpdater", "v2.0.0-adapted").version == "v2.0.0-adapted"


def test_model_updater_unvalidated_candidate_fails():
    registry = ModelRegistry()
    baseline = create_baseline_model()
    updater = ModelUpdater(registry)
    ev = BehaviorEvidence("q0:AUTH", "q0", "AUTH")

    cand_unvalidated = CandidateModel(
        candidate_id="cand_unvalidated",
        parent_version="v1.0.0",
        proposed_transitions=[("q0", "AUTH", "q1", "GRANT")],
        supporting_evidence=ev,
        lifecycle_state=AdaptationState.CANDIDATE,  # Not VALIDATED!
    )

    with pytest.raises(ValueError, match="Cannot update model from candidate in state"):
        updater.apply_update(cand_unvalidated, baseline, "v2.0.0-adapted")
