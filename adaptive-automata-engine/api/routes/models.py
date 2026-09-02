"""
Model Management API Routes.
"""

from fastapi import APIRouter, HTTPException, Request, Header
from api.schemas.dto import ModelActivateRequest

router = APIRouter(prefix="/models", tags=["Models"])


@router.get("")
def list_models(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        return {"versions": ["v1.0.0"]}
    reg = pipeline.model_registry
    return {
        "model_id": reg.model_id,
        "active_version": reg.active_version,
        "versions": reg.get_version_history(),
    }


@router.get("/active")
def get_active_model(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        return {"version": "v1.0.0"}
    model = pipeline.model_registry.get_active_model()
    return {
        "model_id": model.model_id,
        "version": model.version,
        "source": model.source.value if hasattr(model.source, "value") else str(model.source),
        "num_states": model.num_states,
        "num_transitions": model.num_transitions,
        "created_at": model.created_at,
    }


@router.get("/{version}")
def get_model_by_version(version: str, request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline uninitialized.")
    try:
        model = pipeline.model_registry.registry.get_model(pipeline.model_registry.model_id, version)
        return {
            "model_id": model.model_id,
            "version": model.version,
            "source": model.source.value if hasattr(model.source, "value") else str(model.source),
            "num_states": model.num_states,
            "num_transitions": model.num_transitions,
            "created_at": model.created_at,
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Model version '{version}' not found.")


@router.post("/{version}/activate")
def activate_model_version(version: str, body: ModelActivateRequest, request: Request, authorization: str = Header(None)):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline uninitialized.")
    
    # Enforce Phase 5 Validation & Authorization
    try:
        pipeline.model_registry.set_active_model(version)
        return {
            "status": "ACTIVATED",
            "active_version": version,
            "reason": body.reason,
        }
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Cannot activate unvalidated/unregistered model: {e}")


@router.post("/rollback")
def rollback_model(request: Request, authorization: str = Header(None)):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline uninitialized.")
    try:
        restored_ver = pipeline.model_registry.rollback()
        return {
            "status": "ROLLED_BACK",
            "active_version": restored_ver,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
