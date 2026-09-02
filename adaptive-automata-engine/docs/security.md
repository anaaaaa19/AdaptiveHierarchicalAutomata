# Deployment Security Boundaries & Limitations

## Security Boundaries
1. **Untrusted Data Isolation**: Network packets, raw byte payloads, and AI agent text outputs are treated as untrusted input.
2. **Model Activation Protection**: Direct model mutation is forbidden. Models must pass Phase 5 formal validation prior to registry activation.
3. **Frontend Isolation**: The React dashboard is strictly a visualization client with no trusted detection logic.

## Deployment Limitations
- Encrypted payloads (TLS/SSH) require application-level visibility or payload decryption prior to message tokenization.
- High-rate raw socket capture requires appropriate OS privileges (e.g. `CAP_NET_RAW` / Administrator).
- AI agent reasoning is advisory; formal automata and policies maintain final enforcement authority.
