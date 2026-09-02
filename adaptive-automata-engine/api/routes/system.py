"""
System Health and Telemetry API Routes.
"""

from fastapi import APIRouter, Request

router = APIRouter(tags=["System"])


@router.get("/health")
def get_health(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        return {"service": "healthy", "pipeline": "uninitialized"}
    
    checker = getattr(request.app.state, "health_checker", None)
    if checker:
        return checker.check_health()
    return {"service": "healthy", "pipeline": "running"}


@router.get("/status")
def get_status(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        return {"status": "inactive"}
    return {
        "active_model_version": pipeline.model_registry.active_version,
        "queue_depth": pipeline.queue.qsize(),
        "is_capture_active": pipeline.capture_source.is_active,
        "active_sessions_count": len(pipeline.session_manager.list_active_sessions()),
        "metrics": pipeline.metrics.get_summary(),
    }


@router.get("/metrics")
def get_metrics(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        return {}
    return pipeline.metrics.get_summary()
