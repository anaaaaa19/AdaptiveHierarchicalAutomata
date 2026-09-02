"""
Adaptation Lifecycle State Machine.

Enforces explicit, legal state transitions during model adaptation and prevents illegal shortcuts
(e.g., OBSERVED -> ACTIVATED without candidate generation and formal validation).
"""

from enum import Enum


class AdaptationState(str, Enum):
    """Explicit lifecycle states for candidate protocol adaptation."""
    OBSERVED = "OBSERVED"           # Initial observation of behavior
    NOVEL = "NOVEL"                 # Confirmed novel behavior not in model
    UNDER_REVIEW = "UNDER_REVIEW"   # Evidence accumulating in EvidenceStore
    CANDIDATE = "CANDIDATE"         # AdaptationPolicy generated CandidateModel
    VALIDATING = "VALIDATING"       # FormalValidator running regression tests
    VALIDATED = "VALIDATED"         # Formal validation passed cleanly
    ACTIVATED = "ACTIVATED"         # ModelUpdater published new version vN+1
    REJECTED = "REJECTED"           # Policy rejection or validation failure


class InvalidStateTransitionError(Exception):
    """Raised when an illegal adaptation lifecycle state transition is attempted."""
    pass


class AdaptationStateTracker:
    """
    Manages and validates lifecycle state transitions for candidate adaptations.
    """

    # Explicit legal state transition map
    _LEGAL_TRANSITIONS: dict[AdaptationState, set[AdaptationState]] = {
        AdaptationState.OBSERVED: {AdaptationState.NOVEL},
        AdaptationState.NOVEL: {AdaptationState.UNDER_REVIEW, AdaptationState.REJECTED},
        AdaptationState.UNDER_REVIEW: {AdaptationState.CANDIDATE, AdaptationState.REJECTED},
        AdaptationState.CANDIDATE: {AdaptationState.VALIDATING, AdaptationState.REJECTED},
        AdaptationState.VALIDATING: {AdaptationState.VALIDATED, AdaptationState.REJECTED},
        AdaptationState.VALIDATED: {AdaptationState.ACTIVATED, AdaptationState.REJECTED},
        AdaptationState.ACTIVATED: set(),
        AdaptationState.REJECTED: set(),
    }

    def __init__(self, initial_state: AdaptationState = AdaptationState.OBSERVED) -> None:
        self._current_state: AdaptationState = initial_state
        self._history: list[AdaptationState] = [initial_state]

    @property
    def current_state(self) -> AdaptationState:
        """Current lifecycle state."""
        return self._current_state

    @property
    def history(self) -> tuple[AdaptationState, ...]:
        """Chronological audit trace of lifecycle states."""
        return tuple(self._history)

    def transition_to(self, new_state: AdaptationState) -> None:
        """
        Transition to a new lifecycle state.

        Raises:
            InvalidStateTransitionError: If the transition violates legal lifecycle paths.
        """
        allowed = self._LEGAL_TRANSITIONS.get(self._current_state, set())
        if new_state not in allowed:
            raise InvalidStateTransitionError(
                f"Illegal adaptation state transition from '{self._current_state.value}' to '{new_state.value}'. "
                f"Allowed target states: {[s.value for s in allowed]}."
            )
        self._current_state = new_state
        self._history.append(new_state)

    def __repr__(self) -> str:
        return f"AdaptationStateTracker(state={self._current_state.value}, steps={len(self._history)})"
