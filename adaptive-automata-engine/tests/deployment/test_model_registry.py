"""
Tests for DeploymentModelRegistry.
"""

from adaptive_automata.core.mealy import MealyMachine, State
from adaptive_automata.deployment.models.registry import DeploymentModelRegistry
from adaptive_automata.models.versioning import ModelRegistry, VersionedProtocolModel, ModelSource


def test_deployment_model_registry_operations():
    q0 = State("q0", is_initial=True)
    m = MealyMachine[str, str]()
    model = VersionedProtocolModel("m1", "v1.0.0", ModelSource.PASSIVE_INFERENCE, m)

    reg = ModelRegistry()
    reg.register_model(model)
    dep_reg = DeploymentModelRegistry(reg, "m1")

    assert dep_reg.active_version == "v1.0.0"
    active_m = dep_reg.get_active_model()
    assert active_m.version == "v1.0.0"
