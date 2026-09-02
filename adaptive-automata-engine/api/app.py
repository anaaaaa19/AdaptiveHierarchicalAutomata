"""
FastAPI Application Entry Point for Phase 8 Real-Time Deployment Server.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import alerts, events, investigations, models, sessions, system
from adaptive_automata.analysis.analyzer import HierarchicalAnalyzer
from adaptive_automata.core.mealy import MealyMachine, State
from adaptive_automata.deployment.capture.replay import ReplayCaptureSource
from adaptive_automata.deployment.config.settings import DeploymentConfig
from adaptive_automata.deployment.models.registry import DeploymentModelRegistry
from adaptive_automata.deployment.monitoring.health import HealthChecker
from adaptive_automata.deployment.pipeline.realtime import RealTimePipeline
from adaptive_automata.deployment.storage.sqlite import InMemoryEventStore
from adaptive_automata.models.versioning import ModelRegistry, VersionedProtocolModel, ModelSource


def create_pipeline() -> RealTimePipeline:
    """Initialize a default operational deployment pipeline for demonstration/testing."""
    q0 = State("q0", is_initial=True)
    q1 = State("q1")
    mealy = MealyMachine[str, str]()
    mealy.add_transition(q0, "SYN", q1, "SYN-ACK")
    mealy.add_transition(q1, "ACK", q0, "READY")

    init_model = VersionedProtocolModel[str, str](
        model_id="toy_protocol_model",
        version="v1.0.0",
        source=ModelSource.PASSIVE_INFERENCE,
        mealy_machine=mealy,
    )

    model_reg = ModelRegistry()
    model_reg.register_model(init_model)

    dep_model_reg = DeploymentModelRegistry(registry=model_reg, model_id="toy_protocol_model")
    dep_model_reg.set_active_model("v1.0.0")

    analyzer = HierarchicalAnalyzer(fast_path_model=init_model)
    capture = ReplayCaptureSource()
    event_store = InMemoryEventStore()

    config = DeploymentConfig()

    pipeline = RealTimePipeline(
        capture_source=capture,
        analyzer=analyzer,
        model_registry=dep_model_reg,
        config=config,
        event_store=event_store,
    )
    return pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize RealTimePipeline
    pipeline = create_pipeline()
    app.state.pipeline = pipeline
    app.state.health_checker = HealthChecker(
        capture_source=pipeline.capture_source,
        event_store=pipeline.event_store,
        model_registry=pipeline.model_registry,
    )
    yield
    # Shutdown: Cleanup resources
    if hasattr(app.state, "pipeline"):
        app.state.pipeline.stop()
        if app.state.pipeline.event_store:
            app.state.pipeline.event_store.close()


app = FastAPI(
    title="Adaptive Hierarchical Automata Engine - Real-Time Platform API",
    version="8.0.0",
    description="Production Deployment REST & WebSocket API for Protocol Monitoring, Security Detection, and Model Versioning.",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach Routes
app.include_router(system.router)
app.include_router(models.router)
app.include_router(sessions.router)
app.include_router(events.router)
app.include_router(alerts.router)
app.include_router(investigations.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)
