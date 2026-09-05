"""
Real-Time Deployment Pipeline Orchestrator.
"""

from concurrent.futures import ThreadPoolExecutor
import threading
import time
from typing import Any, Callable, Sequence

from adaptive_automata.analysis.analyzer import HierarchicalAnalyzer
from adaptive_automata.adaptation.engine import AdaptiveModelEngine
from adaptive_automata.adaptation.evidence import BehaviorEvidence
from adaptive_automata.adaptation.novelty import NoveltyDetector, NoveltyResult, NoveltyStatus
from adaptive_automata.agents.router import AgentRouter
from adaptive_automata.deployment.alerts.manager import AlertManager
from adaptive_automata.deployment.capture.base import PacketCaptureSource
from adaptive_automata.deployment.config.settings import DeploymentConfig
from adaptive_automata.deployment.messages.extractor import MessageExtractor
from adaptive_automata.deployment.models.registry import DeploymentModelRegistry
from adaptive_automata.deployment.monitoring.metrics import MetricsCollector
from adaptive_automata.deployment.packet.processor import PacketProcessor
from adaptive_automata.deployment.pipeline.events import ProtocolEvent, RawPacket
from adaptive_automata.deployment.pipeline.queue import BoundedEventQueue
from adaptive_automata.deployment.sessions.manager import SessionManager, SessionContext
from adaptive_automata.deployment.storage.base import EventStore
from adaptive_automata.protocol.tokenizer import BaseTokenizer, DelimiterTokenizer, HeaderCommandTokenizer
from adaptive_automata.security.alerts import SecurityAlert
from adaptive_automata.security.assessment import SecurityAssessment
from adaptive_automata.security.behavioral import BehavioralAnalyzer


class RealTimePipeline:
    """
    Top-Level Modular Real-Time Deployment Pipeline.
    
    Data Plane: Capture -> PacketProcessor -> SessionManager -> MessageExtractor ->
                BaseMessageTokenizer -> HierarchicalAnalyzer -> BehavioralAnalyzer.
    Control Plane: EventStore, AlertManager, DeploymentModelRegistry, AdaptiveModelEngine,
                   Async Phase 7 AgentRouter execution.
    """

    def __init__(
        self,
        capture_source: PacketCaptureSource,
        analyzer: HierarchicalAnalyzer,
        model_registry: DeploymentModelRegistry,
        config: DeploymentConfig | None = None,
        behavioral_analyzer: BehavioralAnalyzer | None = None,
        adaptation_engine: AdaptiveModelEngine | None = None,
        agent_router: AgentRouter | None = None,
        event_store: EventStore | None = None,
        alert_manager: AlertManager | None = None,
        tokenizer: BaseMessageTokenizer | None = None,
    ) -> None:
        self.capture_source = capture_source
        self.analyzer = analyzer
        self.model_registry = model_registry
        self.config = config or DeploymentConfig()
        self.behavioral_analyzer = behavioral_analyzer or BehavioralAnalyzer()
        self.adaptation_engine = adaptation_engine
        self.agent_router = agent_router
        self.event_store = event_store
        self.alert_manager = alert_manager or AlertManager(event_store=event_store)
        self.tokenizer = tokenizer or DelimiterTokenizer(delimiter=":")

        self.processor = PacketProcessor(max_payload_bytes=self.config.max_payload_bytes)
        self.session_manager = SessionManager(
            max_inactivity_sec=self.config.max_session_inactivity_sec,
            max_sessions=self.config.max_sessions,
        )
        self.message_extractor = MessageExtractor()
        self.metrics = MetricsCollector()
        self.queue: BoundedEventQueue[RawPacket] = BoundedEventQueue(
            max_size=self.config.max_queue_size,
            policy=self.config.backpressure_policy,
        )

        self._running = False
        self._worker_threads: list[threading.Thread] = []
        self._ai_executor = ThreadPoolExecutor(max_workers=self.config.max_ai_concurrent_jobs)
        self._event_subscribers: list[Callable[[ProtocolEvent], None]] = []

    def subscribe_events(self, callback: Callable[[ProtocolEvent], None]) -> None:
        """Register a callback for real-time event distribution (e.g. WebSockets)."""
        self._event_subscribers.append(callback)

    def process_packet_synchronous(self, raw_pkt: RawPacket) -> list[ProtocolEvent]:
        """
        Synchronously process a single packet through the complete detection pipeline.
        Useful for deterministic testing, offline PCAP replay, and micro-benchmarking.
        """
        start_time = time.time()
        self.metrics.packets_processed += 1
        active_ver = self.model_registry.active_version

        # 1. Packet Processing & Slicing
        proc_pkt = self.processor.process(raw_pkt)

        # 2. Session Reconstruction
        sess_ctx = self.session_manager.get_or_create_session(proc_pkt, active_model_version=active_ver)

        # 3. Protocol Message Extraction
        messages = self.message_extractor.extract(proc_pkt)
        if not messages:
            return []
        self.metrics.messages_processed += len(messages)

        events: list[ProtocolEvent] = []

        # Process each extracted message
        for msg in messages:
            # 4. Tokenization to formal symbols
            if hasattr(self.tokenizer, "tokenize"):
                try:
                    toks = self.tokenizer.tokenize(msg)
                    symbols = [t.value if hasattr(t, "value") else str(t) for t in toks]
                except Exception:
                    symbols = [msg.split(":")[-1].strip()] if ":" in msg else [msg.strip()]
            elif ":" in msg:
                symbols = [msg.split(":")[-1].strip()]
            else:
                symbols = [msg.strip()]
            if not symbols:
                symbols = [msg]

            for sym in symbols:
                sess_ctx.protocol.recent_symbols.append(sym)

                # 5. Hierarchical Formal Automata Analysis (Phase 4 Core)
                # Evaluates sequence using current active model
                self.analyzer.fast_path_model = self.model_registry.get_active_model()
                analysis_res = self.analyzer.analyze_sequence(
                    sess_ctx.protocol.recent_symbols,
                    session_id=sess_ctx.session_id,
                )
                sess_ctx.protocol.current_formal_state = analysis_res.state

                # 6. Novelty Assessment (Phase 5 helper)
                novelty_detector = self.adaptation_engine.novelty_detector if self.adaptation_engine else NoveltyDetector()
                novelty_res = novelty_detector.detect_novelty(analysis_res, self.model_registry.get_active_model())

                # 7. Security Assessment (Phase 6 Core)
                sec_assessment = self.behavioral_analyzer.analyze_security(
                    session=sess_ctx.to_protocol_session(),
                    analysis_result=analysis_res,
                    novelty_result=novelty_res,
                )
                sess_ctx.security.last_assessment_status = sec_assessment.behavioral_classification.value if hasattr(sec_assessment.behavioral_classification, "value") else str(sec_assessment.behavioral_classification)
                sess_ctx.security.highest_severity = sec_assessment.severity.value if hasattr(sec_assessment.severity, "value") else str(sec_assessment.severity)

                # 8. Alert Generation (Phase 6 / Deployment AlertManager)
                alert = self.alert_manager.process_security_assessment(
                    sec_assessment,
                    symbol=sym,
                    state=analysis_res.state,
                )
                if alert:
                    sess_ctx.security.alerts_generated += 1

                # Elapsed Latency
                latency_ms = (time.time() - start_time) * 1000.0

                # Construct ProtocolEvent
                evt_id = f"EVT-{sess_ctx.session_id}-{int(time.time() * 1000000)}"
                event = ProtocolEvent(
                    event_id=evt_id,
                    session_id=sess_ctx.session_id,
                    protocol=proc_pkt.flow_key[4],
                    direction=proc_pkt.direction,
                    symbol=sym,
                    formal_state=analysis_res.state,
                    model_version=active_ver,
                    analysis_result=analysis_res,
                    security_assessment=sec_assessment,
                    processing_latency_ms=latency_ms,
                    raw_payload_snippet=proc_pkt.payload_str[:128],
                )

                # 9. Event Persistence
                if self.event_store:
                    self.event_store.store_event(event)

                # Metrics Update
                level_str = analysis_res.level_used.value if hasattr(analysis_res.level_used, "value") else str(analysis_result.level_used)
                self.metrics.record_event(latency_ms=latency_ms, level_used=level_str, is_alert=alert is not None)

                # 10. Optional Out-of-Band Adaptation Evidence Accumulation (Phase 5)
                if self.adaptation_engine and novelty_status == NoveltyStatus.NOVEL:
                    self._trigger_adaptation_evidence(sess_ctx, analysis_res)

                # 11. Optional Out-of-Band AI Agent Investigation (Phase 7)
                if alert and self.agent_router and self.config.async_ai_enabled:
                    self._dispatch_async_ai_investigation(alert, event)

                # 12. Notify Real-Time Subscribers
                for sub in self._event_subscribers:
                    try:
                        sub(event)
                    except Exception:
                        pass

                events.append(event)

        return events

    def _trigger_adaptation_evidence(self, sess_ctx: SessionContext, analysis_res: Any) -> None:
        """Accumulate evidence in Phase 5 AdaptationEngine out-of-band."""
        try:
            proto_sess = sess_ctx.to_protocol_session()
            self.adaptation_engine.process_session(proto_sess, tokenizer=self.tokenizer)
        except Exception:
            pass

    def _dispatch_async_ai_investigation(self, alert: SecurityAlert, event: ProtocolEvent) -> None:
        """Dispatch Phase 7 AI Router investigation asynchronously to thread pool."""
        def run_ai():
            try:
                ctx = {
                    "session_id": alert.session_id,
                    "event_type": "SECURITY_ALERT",
                    "severity": alert.severity.value if hasattr(alert.severity, "value") else str(alert.severity),
                    "reason_codes": [r.value if hasattr(r, "value") else str(r) for r in alert.reason_codes],
                    "symbol": alert.triggering_symbol,
                    "state": alert.current_state,
                    "model_version": alert.model_version,
                }
                res = self.agent_router.route_and_execute("SECURITY_ALERT", ctx)
                # Store AI findings into alert metadata
                alert.evidence["ai_investigation_id"] = res.investigation_id
                alert.evidence["ai_recommendation"] = res.action_recommendation
                alert.evidence["ai_explanation"] = res.explanation
                if self.event_store:
                    self.event_store.store_alert(alert)
            except Exception as e:
                # Failure isolation: AI errors never crash data plane
                alert.evidence["ai_status"] = "UNAVAILABLE"
                alert.evidence["ai_error"] = str(e)

        self._ai_executor.submit(run_ai)

    def start(self) -> None:
        """Start async pipeline worker threads and packet capture source."""
        self._running = True
        self.capture_source.start()

        for i in range(self.config.num_worker_threads):
            t = threading.Thread(target=self._worker_loop, name=f"PipelineWorker-{i+1}", daemon=True)
            t.start()
            self._worker_threads.append(t)

        # Producer thread feeding queue from capture source
        prod_t = threading.Thread(target=self._capture_producer_loop, name="CaptureProducer", daemon=True)
        prod_t.start()

    def stop(self) -> None:
        """Gracefully stop pipeline and capture source."""
        self._running = False
        self.capture_source.stop()
        for t in self._worker_threads:
            t.join(timeout=1.0)
        self._ai_executor.shutdown(wait=False)

    def _capture_producer_loop(self) -> None:
        for raw_pkt in self.capture_source.packets():
            if not self._running:
                break
            added = self.queue.put(raw_pkt)
            if not added:
                self.metrics.record_dropped_event(1)
            self.metrics.set_queue_depth(self.queue.qsize())

    def _worker_loop(self) -> None:
        while self._running:
            raw_pkt = self.queue.get(timeout=0.1)
            if raw_pkt:
                self.metrics.set_queue_depth(self.queue.qsize())
                self.process_packet_synchronous(raw_pkt)

    def run_replay(self, max_packets: int | None = None) -> list[ProtocolEvent]:
        """
        Run offline replay synchronously to process all packets from capture source.
        Returns list of all generated ProtocolEvents.
        """
        events: list[ProtocolEvent] = []
        self.capture_source.start()
        count = 0
        for raw_pkt in self.capture_source.packets():
            count += 1
            if max_packets and count > max_packets:
                break
            evs = self.process_packet_synchronous(raw_pkt)
            events.extend(evs)
        self.capture_source.stop()
        return events
