"""
Abstract Base Event Store Interface.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from adaptive_automata.deployment.pipeline.events import ProtocolEvent
from adaptive_automata.security.alerts import SecurityAlert


class EventStore(ABC):
    """
    Abstract interface for storing and retrieving ProtocolEvents and SecurityAlerts.
    Decouples core analysis logic from persistent database engines.
    """

    @abstractmethod
    def store_event(self, event: ProtocolEvent) -> None:
        """Persist a single ProtocolEvent."""
        pass

    @abstractmethod
    def store_alert(self, alert: SecurityAlert) -> None:
        """Persist a single SecurityAlert."""
        pass

    @abstractmethod
    def get_event(self, event_id: str) -> ProtocolEvent | None:
        """Retrieve ProtocolEvent by event_id."""
        pass

    @abstractmethod
    def get_alert(self, alert_id: str) -> SecurityAlert | None:
        """Retrieve SecurityAlert by alert_id."""
        pass

    @abstractmethod
    def list_events(
        self,
        session_id: str | None = None,
        model_version: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ProtocolEvent]:
        """List stored ProtocolEvents with optional filtering."""
        pass

    @abstractmethod
    def list_alerts(
        self,
        severity: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SecurityAlert]:
        """List stored SecurityAlerts with optional filtering."""
        pass

    @abstractmethod
    def get_event_count(self) -> int:
        """Total number of stored events."""
        pass

    @abstractmethod
    def get_alert_count(self) -> int:
        """Total number of stored alerts."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close storage connections and flush resources."""
        pass
