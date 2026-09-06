"""
Data Transfer Objects (DTOs) for API Endpoints.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class ModelActivateRequest(BaseModel):
    version: str = Field(..., description="Model version string to activate.")
    reason: str = Field("Manual operator activation request", description="Reason for model activation.")


class AlertStatusUpdateRequest(BaseModel):
    status: Optional[str] = Field(None, description="New alert status (NEW, ACKNOWLEDGED, INVESTIGATING, RESOLVED, FALSE_POSITIVE).")
    state: Optional[str] = Field(None, description="New alert state (alias for status).")
    notes: Optional[str] = Field(None, description="Operator notes for status change.")


class InvestigationRunRequest(BaseModel):
    alert_id: str = Field(..., description="Target alert ID to investigate.")
    event_context: Optional[dict[str, Any]] = Field(default_factory=dict, description="Context parameters for investigation.")
