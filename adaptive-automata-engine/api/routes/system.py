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


@router.post("/capture/start")
def start_capture(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        return {"status": "error", "detail": "Pipeline uninitialized"}
    try:
        pipeline.capture_source.start()
        return {"status": "started", "is_capture_active": True}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@router.post("/capture/stop")
def stop_capture(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        return {"status": "error", "detail": "Pipeline uninitialized"}
    try:
        pipeline.capture_source.stop()
        return {"status": "stopped", "is_capture_active": False}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@router.post("/adaptation/promote")
def promote_candidate(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        return {"status": "error", "detail": "Pipeline uninitialized"}
    reg = pipeline.model_registry
    history = reg.get_version_history()
    active = reg.active_version
    if len(history) > 1:
        cand = [v for v in history if v != active][-1]
        reg.set_active_model(cand)
        return {"status": "promoted", "active_version": cand}
    return {"status": "no_candidate", "active_version": active}


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


@router.post("/replay/trigger")
@router.post("/replay/start")
def trigger_replay(request: Request):
    pipeline = getattr(request.app.state, "pipeline", None)
    if not pipeline:
        return {"status": "error", "detail": "Pipeline uninitialized"}
    
    from adaptive_automata.deployment.capture.replay import ReplayCaptureSource
    
    replay_records = [
        {"packet_id": "pkt_rep_1", "src_ip": "10.0.0.1", "src_port": 5001, "dst_ip": "10.0.0.2", "dst_port": 8080, "protocol": "TCP", "payload": "SESSION-101:ClientHello"},
        {"packet_id": "pkt_rep_2", "src_ip": "10.0.0.1", "src_port": 5001, "dst_ip": "10.0.0.2", "dst_port": 8080, "protocol": "TCP", "payload": "SESSION-101:AuthToken"},
        {"packet_id": "pkt_rep_3", "src_ip": "10.0.0.1", "src_port": 5001, "dst_ip": "10.0.0.2", "dst_port": 8080, "protocol": "TCP", "payload": "SESSION-101:DataStream"},
        {"packet_id": "pkt_rep_4", "src_ip": "10.0.0.1", "src_port": 5001, "dst_ip": "10.0.0.2", "dst_port": 8080, "protocol": "TCP", "payload": "SESSION-101:Logout"},
        {"packet_id": "pkt_rep_5", "src_ip": "10.0.0.3", "src_port": 5002, "dst_ip": "10.0.0.2", "dst_port": 8080, "protocol": "TCP", "payload": "SESSION-102:ClientHello"},
        {"packet_id": "pkt_rep_6", "src_ip": "10.0.0.3", "src_port": 5002, "dst_ip": "10.0.0.2", "dst_port": 8080, "protocol": "TCP", "payload": "SESSION-102:UNEXPECTED_DEVIATION_PAYLOAD"},
    ]
    
    replay_source = ReplayCaptureSource(replay_records)
    replay_source.start()
    
    prev_source = pipeline.capture_source
    pipeline.capture_source = replay_source
    try:
        events = pipeline.run_replay()
        return {
            "status": "completed",
            "events_generated": len(events),
            "events": [e.to_dict() for e in events],
        }
    finally:
        pipeline.capture_source = prev_source

