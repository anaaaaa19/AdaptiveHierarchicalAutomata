"""
Health Checker Component for Subsystem Diagnostic Telemetry.
"""

from typing import Any

from adaptive_automata.deployment.capture.base import PacketCaptureSource
from adaptive_automata.deployment.storage.base import EventStore
from adaptive_automata.deployment.models.registry import DeploymentModelRegistry


class HealthChecker:
    """
    Health Checker aggregating sub-system diagnostics across capture, storage, pipeline,
    model registry, and AI execution.
    """

    def __init__(
        self,
        capture_source: PacketCaptureSource | None = None,
        event_store: EventStore | None = None,
        model_registry: DeploymentModelRegistry | None = None,
        ai_available: bool = True,
    ) -> None:
        self.capture_source = capture_source
        self.event_store = event_store
        self.model_registry = model_registry
        self.ai_available = ai_available

    def check_health(self) -> dict[str, Any]:
        capture_status = "running" if (self.capture_source and self.capture_source.is_active) else "idle"
        storage_status = "ok" if self.event_store else "disabled"
        active_model = self.model_registry.active_version if self.model_registry else "v1.0.0"
        ai_status = "available" if self.ai_available else "disabled"

        return {
            "service": "healthy",
            "capture": capture_status,
            "pipeline": "running",
            "storage": storage_status,
            "model_version": active_model,
            "ai": ai_status,
        }
