"""
Phase 8 Zero-Downtime Model Hot-Reload and Version Provenance Test.
"""

from adaptive_automata.core.mealy import MealyMachine, State
from adaptive_automata.deployment.models.registry import DeploymentModelRegistry
from adaptive_automata.models.versioning import ModelRegistry, VersionedProtocolModel, ModelSource


def run_model_switch_test():
    print("Testing Model Registry Hot-Reload & Rollback...")
    q0 = State("q0", is_initial=True)
    q1 = State("q1")

    m1 = MealyMachine[str, str]()
    m1.add_transition(q0, "SYN", q1, "SYN-ACK")

    model_v1 = VersionedProtocolModel[str, str]("model1", "v1.0.0", ModelSource.PASSIVE_INFERENCE, m1)

    m2 = MealyMachine[str, str]()
    m2.add_transition(q0, "SYN", q1, "SYN-ACK")
    m2.add_transition(q1, "CAPABILITIES", q0, "ACK")

    model_v2 = VersionedProtocolModel[str, str]("model1", "v2.0.0-adapted", ModelSource.PROTOCOL_EVOLUTION, m2)

    reg = ModelRegistry()
    reg.register_model(model_v1)
    reg.register_model(model_v2)

    dep_reg = DeploymentModelRegistry(registry=reg, model_id="model1")
    dep_reg.set_active_model("v1.0.0")
    assert dep_reg.active_version == "v1.0.0"

    dep_reg.set_active_model("v2.0.0-adapted")
    assert dep_reg.active_version == "v2.0.0-adapted"

    restored = dep_reg.rollback()
    assert restored == "v1.0.0"
    assert dep_reg.active_version == "v1.0.0"

    print("Model Hot-Reload and Rollback verified successfully!")


if __name__ == "__main__":
    run_model_switch_test()
