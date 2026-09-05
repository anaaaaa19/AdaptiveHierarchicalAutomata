# Phase 8 Deployment Architecture

## System Overview

The Phase 8 Deployment Platform decouples system operation into a high-throughput **Data Plane** and an extensible **Control Plane**.

```
LIVE TRAFFIC / PCAP -> PacketCaptureSource -> PacketProcessor -> SessionManager ->
MessageExtractor -> BaseMessageTokenizer -> HierarchicalAnalyzer (Phase 4) ->
BehavioralAnalyzer (Phase 6) -> EventStore / AlertManager -> REST/WS API -> Dashboard
```

## Security & Architectural Constraints

1. **Data Plane Isolation**: High-frequency packet processing runs independently from storage serialization and AI agent execution.
2. **Phase 5 Adaptation Safety**: Model updates require passing Phase 5 `FormalValidator` regression tests prior to `ModelRegistry` activation.
3. **Phase 7 AI Async Execution**: AI agents run strictly out-of-band. AI timeouts or failures emit `FORMAL_ONLY_FALLBACK` records without dropping packets.
