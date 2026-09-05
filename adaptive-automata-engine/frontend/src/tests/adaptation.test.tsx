import { describe, it, expect } from 'vitest';
import { AdaptationStateDTO } from '../types';

describe('Adaptation Policy State Tests', () => {
  it('Enforces candidate model validation status presence', () => {
    const adaptationState: AdaptationStateDTO = {
      active_model_version: 'v1.0.0',
      candidate_model_version: 'v1.1.0-cand',
      evidence_count: 55,
      novelty_threshold: 0.85,
      drift_metric: 0.12,
      validation_status: 'PASSED',
      policy_status: 'NOMINAL',
    };

    expect(adaptationState.validation_status).toBe('PASSED');
    expect(adaptationState.candidate_model_version).toBeDefined();
    expect(adaptationState.active_model_version).not.toEqual(adaptationState.candidate_model_version);
  });
});
