"""Unit tests for ModelRollbackManager and RollbackEvent."""

import pytest
from adaptive_automata.core import State, MealyMachine
from adaptive_automata.models import ModelSource, VersionedProtocolModel, ModelRegistry
from adaptive_automata.adaptation.rollback import ModelRollbackManager


def create_model(version: str) -> VersionedProtocolModel[str, str]:
    s0 = State("q0", is_initial=True)
    mealy = MealyMachine[str, str]("TestRollback")
    mealy.add_state(s0)
    return VersionedProtocolModel[str, str](
        model_id="TestRollback",
        version=version,
        source=ModelSource.ACTIVE_HYBRID,
        mealy_machine=mealy,
    )


def test_rollback_manager_flow():
    registry = ModelRegistry()
    m1 = create_model("v1.0.0")
    m2 = create_model("v2.0.0")
    registry.register_model(m1)
    registry.register_model(m2)

    manager = ModelRollbackManager(registry)
    manager.set_active_version("TestRollback", "v2.0.0")
    assert manager.get_active_version("TestRollback") == "v2.0.0"

    # Execute rollback to v1.0.0
    reactivated = manager.rollback("TestRollback", "v1.0.0", reason="Audit triggered rollback")
    assert reactivated.version == "v1.0.0"
    assert manager.get_active_version("TestRollback") == "v1.0.0"
    assert len(manager.audit_log) == 1
    assert manager.audit_log[0].from_version == "v2.0.0"
    assert manager.audit_log[0].to_version == "v1.0.0"


def test_rollback_to_invalid_version_raises_keyerror():
    registry = ModelRegistry()
    m1 = create_model("v1.0.0")
    registry.register_model(m1)

    manager = ModelRollbackManager(registry)
    manager.set_active_version("TestRollback", "v1.0.0")

    with pytest.raises(KeyError, match="No model found"):
        manager.rollback("TestRollback", "v9.9.9", reason="Non-existent version")
