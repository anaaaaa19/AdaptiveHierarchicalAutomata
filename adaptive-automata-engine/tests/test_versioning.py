"""Unit tests for Model Versioning and ModelRegistry."""

import pytest
from adaptive_automata.core import State, MealyMachine
from adaptive_automata.models import ModelSource, VersionedProtocolModel, ModelRegistry


def test_model_registry_immutability():
    s0 = State("s0", is_initial=True)
    mealy = MealyMachine[str, str]("TestMealy")
    mealy.add_state(s0)
    mealy.validate()

    model_v1 = VersionedProtocolModel[str, str](
        model_id="ProtoA",
        version="v1.0.0",
        source=ModelSource.PASSIVE_INFERENCE,
        mealy_machine=mealy,
    )

    registry = ModelRegistry()
    registry.register_model(model_v1)

    assert registry.get_model("ProtoA", "v1.0.0").version == "v1.0.0"
    assert registry.list_versions("ProtoA") == ["v1.0.0"]

    # Attempting to register same version must raise ValueError
    with pytest.raises(ValueError, match="already registered"):
        registry.register_model(model_v1)

    # Register new version
    model_v2 = VersionedProtocolModel[str, str](
        model_id="ProtoA",
        version="v2.0.0",
        source=ModelSource.PROTOCOL_EVOLUTION,
        mealy_machine=mealy,
    )
    registry.register_model(model_v2)

    assert registry.list_versions("ProtoA") == ["v1.0.0", "v2.0.0"]
    assert registry.get_latest_model("ProtoA").version == "v2.0.0"
