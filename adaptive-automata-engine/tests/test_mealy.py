import pytest
from adaptive_automata.core import State, MealyMachine, MealyMachineValidationError, InvalidMealyStateError


def test_mealy_transduction():
    s0 = State("LOCKED", is_initial=True)
    s1 = State("UNLOCKED")

    mealy = MealyMachine[str, str]("DoorController")
    mealy.add_transition(s0, "PIN_CORRECT", s1, "UNLOCK_SERVO")
    mealy.add_transition(s0, "PIN_WRONG", s0, "ALARM")
    mealy.add_transition(s1, "LOCK_CMD", s0, "LOCK_SERVO")

    mealy.validate()

    outputs, final_state = mealy.process_sequence(["PIN_WRONG", "PIN_CORRECT", "LOCK_CMD"])

    assert outputs == ["ALARM", "UNLOCK_SERVO", "LOCK_SERVO"]
    assert final_state == s0


def test_mealy_conflicting_transitions():
    s0 = State("S0", is_initial=True)
    s1 = State("S1")
    s2 = State("S2")

    mealy = MealyMachine[str, str]()
    mealy.add_transition(s0, "IN", s1, "OUT1")

    with pytest.raises(MealyMachineValidationError, match="Conflicting Mealy transition"):
        mealy.add_transition(s0, "IN", s2, "OUT2")


def test_mealy_undefined_step():
    s0 = State("S0", is_initial=True)
    mealy = MealyMachine[str, str]()
    mealy.add_state(s0)

    with pytest.raises(InvalidMealyStateError, match="Undefined Mealy transition"):
        mealy.step("UNKNOWN")
