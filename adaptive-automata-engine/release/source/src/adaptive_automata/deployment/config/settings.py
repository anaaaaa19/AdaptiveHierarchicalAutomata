"""
Centralized Configuration Settings for Phase 8 Real-Time Deployment.
"""

from dataclasses import dataclass, field
from enum import Enum
import os
from typing import Any


class OperationalMode(str, Enum):
    """Execution mode of the deployment pipeline."""
    RESEARCH_MODE = "RESEARCH_MODE"
    DEPLOYMENT_MODE = "DEPLOYMENT_MODE"


class BackpressurePolicy(str, Enum):
    """Backpressure handling policy when event queue exceeds threshold."""
    DROP_OLDEST = "DROP_OLDEST"
    DROP_NEWEST = "DROP_NEWEST"
    BLOCK = "BLOCK"
    SAMPLE = "SAMPLE"


@dataclass
class DeploymentConfig:
    """
    Configuration parameters for live/replay deployment pipeline, storage,
    API, alerting, resource limits, and AI execution.
    """
    mode: OperationalMode = field(
        default_factory=lambda: OperationalMode(os.getenv("MODE", OperationalMode.DEPLOYMENT_MODE.value))
    )
    
    # Capture & Packet Settings
    interface: str = field(default_factory=lambda: os.getenv("CAPTURE_INTERFACE", "eth0"))
    max_payload_bytes: int = 4096
    max_session_inactivity_sec: float = 300.0
    max_sessions: int = 10000
    
    # Queue & Concurrency
    max_queue_size: int = 5000
    backpressure_policy: BackpressurePolicy = field(
        default_factory=lambda: BackpressurePolicy(os.getenv("BACKPRESSURE_POLICY", BackpressurePolicy.DROP_OLDEST.value))
    )
    num_worker_threads: int = 2
    
    # Storage Settings
    storage_type: str = field(default_factory=lambda: os.getenv("STORAGE_TYPE", "sqlite"))
    sqlite_db_path: str = field(default_factory=lambda: os.getenv("SQLITE_DB_PATH", ":memory:"))
    max_event_history: int = 100000
    max_alert_history: int = 10000
    
    # API & WebSocket
    api_host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    api_secret_key: str = field(default_factory=lambda: os.getenv("API_SECRET_KEY", "dev-secret-key-change-in-prod"))
    
    # Alerting & Adaptation
    alert_deduplication_window_sec: float = 60.0
    auto_adaptation_enabled: bool = field(
        default_factory=lambda: os.getenv("AUTO_ADAPTATION_ENABLED", "false").lower() == "true"
    )
    
    # AI Execution
    async_ai_enabled: bool = field(
        default_factory=lambda: os.getenv("ASYNC_AI_ENABLED", "true").lower() == "true"
    )
    max_ai_concurrent_jobs: int = 4
    ai_timeout_sec: float = 10.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode.value,
            "interface": self.interface,
            "max_payload_bytes": self.max_payload_bytes,
            "max_session_inactivity_sec": self.max_session_inactivity_sec,
            "max_sessions": self.max_sessions,
            "max_queue_size": self.max_queue_size,
            "backpressure_policy": self.backpressure_policy.value,
            "num_worker_threads": self.num_worker_threads,
            "storage_type": self.storage_type,
            "sqlite_db_path": self.sqlite_db_path,
            "max_event_history": self.max_event_history,
            "max_alert_history": self.max_alert_history,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "alert_deduplication_window_sec": self.alert_deduplication_window_sec,
            "auto_adaptation_enabled": self.auto_adaptation_enabled,
            "async_ai_enabled": self.async_ai_enabled,
            "max_ai_concurrent_jobs": self.max_ai_concurrent_jobs,
            "ai_timeout_sec": self.ai_timeout_sec,
        }
