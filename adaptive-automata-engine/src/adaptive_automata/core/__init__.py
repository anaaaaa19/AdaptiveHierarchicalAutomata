"""Core automata models and primitives."""

from .state import State
from .transition import Transition, MealyTransition
from .dfa import DFA, DFAValidationError, InvalidStateError
from .mealy import MealyMachine, MealyMachineValidationError, InvalidMealyStateError

__all__ = [
    "State",
    "Transition",
    "MealyTransition",
    "DFA",
    "DFAValidationError",
    "InvalidStateError",
    "MealyMachine",
    "MealyMachineValidationError",
    "InvalidMealyStateError",
]
