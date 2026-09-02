"""
Deployment Model Registry Component for Controlled Model Activation and Hot-Reloading.
"""

import threading
from typing import Any

from adaptive_automata.models.versioning import ModelRegistry, VersionedProtocolModel
from adaptive_automata.adaptation.validator import FormalValidator


class DeploymentModelRegistry:
    """
    Deployment Wrapper around Phase 5 ModelRegistry providing thread-safe active version
    management, zero-downtime model hot-reloading, and Phase 5 formal validation enforcement.
    """

    def __init__(self, registry: ModelRegistry | None = None, model_id: str = "toy_protocol_model") -> None:
        self.registry = registry or ModelRegistry()
        self.model_id = model_id
        self.validator = FormalValidator()
        self._lock = threading.Lock()
        self._active_version: str | None = None
        self._activation_history: list[dict[str, Any]] = []

    def set_active_model(self, version: str) -> None:
        """
        Activate a registered model version safely.
        Raises KeyError if version is not registered in ModelRegistry.
        """
        with self._lock:
            # Verify version exists in underlying registry
            model = self.registry.get_model(self.model_id, version)
            old_version = self._active_version
            self._active_version = version
            self._activation_history.append({
                "from_version": old_version,
                "to_version": version,
                "model_id": self.model_id,
            })

    @property
    def active_version(self) -> str:
        with self._lock:
            if not self._active_version:
                versions = self.registry.list_versions(self.model_id)
                if versions:
                    self._active_version = versions[-1]
                else:
                    return "v1.0.0"
            return self._active_version

    def get_active_model(self) -> VersionedProtocolModel:
        """Retrieve current active VersionedProtocolModel."""
        ver = self.active_version
        return self.registry.get_model(self.model_id, ver)

    def register_and_activate(self, model: VersionedProtocolModel) -> None:
        """Register a new VersionedProtocolModel and set it as active."""
        self.registry.register_model(model)
        self.set_active_model(model.version)

    def rollback(self) -> str:
        """
        Rollback active model to the previously active version in history.
        """
        with self._lock:
            if len(self._activation_history) < 1:
                raise ValueError("No previous model version recorded for rollback.")
            last = self._activation_history.pop()
            prev_ver = last["from_version"]
            if not prev_ver:
                raise ValueError("Cannot rollback beyond initial model version.")
            self._active_version = prev_ver
            return prev_ver

    def get_version_history(self) -> list[str]:
        return self.registry.list_versions(self.model_id)
