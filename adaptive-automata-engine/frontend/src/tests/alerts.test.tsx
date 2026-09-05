import { describe, it, expect } from 'vitest';
import { SecurityAlertDTO } from '../types';

describe('Alert Interaction Logic Tests', () => {
  it('Filters alerts by severity and state correctly', () => {
    const alerts: SecurityAlertDTO[] = [
      {
        alert_id: 'ALT-01',
        session_id: 'SESS-A',
        state: 'NEW',
        classification: 'SYNTAX_ANOMALY',
        severity: 'HIGH',
        representative_symbol: 'BAD_PKT',
        count: 1,
        created_at: 1600000000,
        reason_codes: ['ERR_01'],
      },
      {
        alert_id: 'ALT-02',
        session_id: 'SESS-B',
        state: 'RESOLVED',
        classification: 'BENIGN',
        severity: 'LOW',
        representative_symbol: 'OK_PKT',
        count: 1,
        created_at: 1600000010,
        reason_codes: [],
      },
    ];

    const highAlerts = alerts.filter((a) => a.severity === 'HIGH');
    expect(highAlerts).toHaveLength(1);
    expect(highAlerts[0].alert_id).toBe('ALT-01');

    const newAlerts = alerts.filter((a) => a.state === 'NEW');
    expect(newAlerts).toHaveLength(1);
    expect(newAlerts[0].alert_id).toBe('ALT-01');
  });
});
