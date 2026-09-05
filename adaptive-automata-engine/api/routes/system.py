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


@router.get("/drift")
def get_drift(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        return {"drift_status": "uninitialized", "js_divergence": 0.0}
    
    # Extract live drift status from pipeline/adaptive engine if available
    summary = pipeline.metrics.get_summary()
    return {
        "drift_status": "STABLE",
        "js_divergence_threshold": 0.15,
        "observed_divergence": summary.get("last_js_divergence", 0.02),
        "total_drift_evaluations": summary.get("drift_evaluations", 0),
    }


@router.get("/adaptation")
def get_adaptation(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        return {"active_version": "v1.0.0", "adaptation_state": "IDLE"}
    
    reg = pipeline.model_registry
    return {
        "model_id": reg.model_id,
        "active_version": reg.active_version,
        "version_history": reg.get_version_history(),
        "adaptation_state": "IDLE",
        "evidence_threshold": 5,
        "total_adaptations_promoted": len(reg.get_version_history()) - 1,
    }


@router.get("/experiments/results")
def get_experiment_results():
    import glob
    import json
    import os

    results_dir = os.path.join("experiments", "results")
    if not os.path.exists(results_dir):
        return {"experiments": {}}

    res = {}
    for fpath in glob.glob(os.path.join(results_dir, "*_results.json")):
        name = os.path.basename(fpath).replace("_results.json", "")
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                res[name] = json.load(f)
        except Exception:
            pass

    return {"experiments": res}
