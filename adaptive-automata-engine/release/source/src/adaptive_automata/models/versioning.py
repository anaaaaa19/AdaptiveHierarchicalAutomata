"""
Model Versioning and Immutable Model Registry.

Provides VersionedProtocolModel container for wrapping Mealy machines with metadata,
metrics, and confidence scores, and an immutable ModelRegistry preventing silent overwrites.
"""

from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import threading
from typing import Any, Generic, TypeVar

from adaptive_automata.core.mealy import MealyMachine
from adaptive_automata.learning.confidence import TransitionMetadata

SymbolT = TypeVar("SymbolT")
OutputT = TypeVar("OutputT")


class ModelSource(str, Enum):
    """Origin source of inferred protocol automaton model."""
    PASSIVE_INFERENCE = "PASSIVE_INFERENCE"
    ACTIVE_HYBRID = "ACTIVE_HYBRID"
    PROTOCOL_EVOLUTION = "PROTOCOL_EVOLUTION"


@dataclass(slots=True)
class VersionedProtocolModel(Generic[SymbolT, OutputT]):
    """
    Immutable container encapsulating an inferred protocol Mealy machine,
    version metadata, transition confidence metrics, and evaluation metrics.
    """
    model_id: str
    version: str
    source: ModelSource
    mealy_machine: MealyMachine[SymbolT, OutputT]
    transition_metadata: dict[tuple[str, str], TransitionMetadata] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def num_states(self) -> int:
        return len(self.mealy_machine.states)

    @property
    def num_transitions(self) -> int:
        return len(self.mealy_machine._transitions)

    @property
    def num_unexplored_transitions(self) -> int:
        count = 0
        alphabet_size = len(self.mealy_machine.input_alphabet)
        expected_total = self.num_states * alphabet_size
        actual = self.num_transitions
        diff = max(0, expected_total - actual)

        for meta in self.transition_metadata.values():
            if meta.observation_count == 0:
                count += 1
        return count + diff


class ModelRegistry:
    """
    Registry for storing and retrieving VersionedProtocolModel instances.
    Enforces immutability: attempts to overwrite an existing version will raise ValueError.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._registry: dict[tuple[str, str], VersionedProtocolModel] = {}

    def register_model(self, model: VersionedProtocolModel) -> None:
        """
        Register a new versioned protocol model.

        Raises:
            ValueError: If a model with the same (model_id, version) is already registered.
        """
        with self._lock:
            key = (model.model_id, model.version)
            if key in self._registry:
                raise ValueError(
                    f"Model version '{model.version}' for model '{model.model_id}' is already registered. "
                    f"Silent overwriting of protocol models is strictly forbidden."
                )
            self._registry[key] = model

    def get_model(self, model_id: str, version: str) -> VersionedProtocolModel:
        """Retrieve registered model by ID and version."""
        with self._lock:
            key = (model_id, version)
            if key not in self._registry:
                raise KeyError(f"No model found for ID '{model_id}' version '{version}'.")
            return self._registry[key]

    def list_versions(self, model_id: str) -> list[str]:
        """List all registered version strings for a given model ID."""
        with self._lock:
            return [ver for (m_id, ver) in self._registry.keys() if m_id == model_id]

    def get_latest_model(self, model_id: str) -> VersionedProtocolModel:
        """Retrieve the most recently registered model version for model_id."""
        versions = self.list_versions(model_id)
        if not versions:
            raise KeyError(f"No models registered for ID '{model_id}'.")
        latest_ver = versions[-1]
        return self.get_model(model_id, latest_ver)
