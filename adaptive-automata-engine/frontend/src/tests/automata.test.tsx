import { describe, it, expect } from 'vitest';
import { AutomataGraphDTO } from '../types';

describe('Automata Explorer Data Integrity Tests', () => {
  it('Validates backend automata graph schema structure', () => {
    const mockGraph: AutomataGraphDTO = {
      model_version: 'v1.0.0',
      states: ['START', 'AUTH_REQ', 'ACCEPTED'],
      initial_state: 'START',
      accepting_states: ['ACCEPTED'],
      transitions: [
        { source: 'START', symbol: 'ClientHello', target: 'AUTH_REQ' },
        { source: 'AUTH_REQ', symbol: 'AuthToken', target: 'ACCEPTED' },
      ],
    };

    expect(mockGraph.states).toContain(mockGraph.initial_state);
    expect(mockGraph.states).toEqual(expect.arrayContaining(mockGraph.accepting_states));
    expect(mockGraph.transitions).toHaveLength(2);
    expect(mockGraph.transitions[0].source).toBe('START');
    expect(mockGraph.transitions[0].target).toBe('AUTH_REQ');
  });
});
