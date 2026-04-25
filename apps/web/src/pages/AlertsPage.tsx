const MOCK_ALERTS = [
  { id: 'A01', txn: 'TXN-7a3f2', bank: 'HDFC Bank', risk: 'critical', score: 0.96, time: '2 min ago' },
  { id: 'A02', txn: 'TXN-9b1c8', bank: 'Axis Bank', risk: 'high', score: 0.78, time: '15 min ago' },
  { id: 'A03', txn: 'TXN-4e2d1', bank: 'ICICI Bank', risk: 'high', score: 0.71, time: '1h ago' },
  { id: 'A04', txn: 'TXN-8f5a3', bank: 'SBI', risk: 'medium', score: 0.52, time: '3h ago' },
]

const riskClass: Record<string, string> = {
  critical: 'badge--danger',
  high: 'badge--warning',
  medium: 'badge--info',
}

export default function AlertsPage() {
  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Fraud Alerts</h1>
        <p>Real-time fraud alerts from the scoring engine and WebSocket stream.</p>
      </div>

      <div className="stat-grid" style={{ marginBottom: '2rem' }}>
        <div className="stat-card stat-card--red">
          <div className="stat-card__icon">🔴</div>
          <div className="stat-card__value">4</div>
          <div className="stat-card__label">Active Alerts</div>
        </div>
        <div className="stat-card stat-card--blue">
          <div className="stat-card__icon">📡</div>
          <div className="stat-card__value">Live</div>
          <div className="stat-card__label">WebSocket Status</div>
        </div>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Alert ID</th>
              <th>Transaction</th>
              <th>Bank</th>
              <th>Risk Tier</th>
              <th>Fraud Score</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {MOCK_ALERTS.map((a) => (
              <tr key={a.id}>
                <td style={{ fontFamily: 'var(--font-mono)' }}>{a.id}</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>{a.txn}</td>
                <td>{a.bank}</td>
                <td><span className={`badge ${riskClass[a.risk] || 'badge--info'}`}>{a.risk}</span></td>
                <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{a.score.toFixed(2)}</td>
                <td style={{ color: 'var(--color-text-muted)' }}>{a.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
