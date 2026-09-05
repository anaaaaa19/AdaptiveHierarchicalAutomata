"""
Model Rollback Manager component.

Manages active model version pointers and auditable RollbackEvents, supporting safe rollback
(e.g., v3 -> v2) without deleting past models.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from adaptive_automata.models.versioning import ModelRegistry, VersionedProtocolModel


@dataclass(frozen=True, slots=True)
class RollbackEvent:
    """
    Auditable log event emitted when a model version rollback occurs.
    """
    model_id: str
    from_version: str
    to_version: str
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __repr__(self) -> str:
        return (
            f"RollbackEvent(model='{self.model_id}', {self.from_version} -> {self.to_version}, "
            f"reason='{self.reason}')"
        )


class ModelRollbackManager:
    """
    Manages active model pointers and rollback audit logs.
    """

    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry
        self._active_versions: dict[str, str] = {}
        self._audit_log: list[RollbackEvent] = []

    @property
    def audit_log(self) -> tuple[RollbackEvent, ...]:
        """Audit trail of all rollback events."""
        return tuple(self._audit_log)

    def set_active_version(self, model_id: str, version: str) -> None:
        """Set the active version pointer for a model_id."""
        # Verify model version exists in registry
        _ = self.registry.get_model(model_id, version)
        self._active_versions[model_id] = version

    def get_active_version(self, model_id: str) -> str:
        """Retrieve the active version string for a model_id."""
        if model_id not in self._active_versions:
            # Default to latest registered version in registry
            return self.registry.get_latest_model(model_id).version
        return self._active_versions[model_id]

    def get_active_model(self, model_id: str) -> VersionedProtocolModel[str, str]:
        """Retrieve the active VersionedProtocolModel for a model_id."""
        ver = self.get_active_version(model_id)
        return self.registry.get_model(model_id, ver)

    def rollback(self, model_id: str, target_version: str, reason: str) -> VersionedProtocolModel[str, str]:
        """
        Rollback active model to a previous registered version.

        Returns:
            Re-activated target VersionedProtocolModel.
        """
        curr_ver = self.get_active_version(model_id)
        target_model = self.registry.get_model(model_id, target_version)

        self._active_versions[model_id] = target_version
        event = RollbackEvent(
            model_id=model_id,
            from_version=curr_ver,
            to_version=target_version,
            reason=reason,
        )
        self._audit_log.append(event)
        return target_model
