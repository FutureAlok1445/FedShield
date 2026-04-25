const MOCK_EVENTS = [
  { id: 'PE01', bank: 'Kotak Bank', round: 21, type: 'gradient_scaling', score: 0.91, method: 'fltrust', resolved: false },
  { id: 'PE02', bank: 'Unknown-B007', round: 19, type: 'sign_flip', score: 0.87, method: 'cosine_similarity', resolved: true },
  { id: 'PE03', bank: 'Axis Bank', round: 17, type: 'backdoor', score: 0.83, method: 'norm_check', resolved: true },
]

export default function SecurityPage() {
  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Security — Poisoning Detection</h1>
        <p>Monitor and respond to adversarial model poisoning attacks across the federated network.</p>
      </div>

      <div className="stat-grid">
        <div className="stat-card stat-card--red">
          <div className="stat-card__icon">☠️</div>
          <div className="stat-card__value">7</div>
          <div className="stat-card__label">Poisoning Events (30d)</div>
        </div>
        <div className="stat-card stat-card--green">
          <div className="stat-card__icon">✅</div>
          <div className="stat-card__value">100%</div>
          <div className="stat-card__label">Detection Rate</div>
        </div>
        <div className="stat-card stat-card--blue">
          <div className="stat-card__icon">🔗</div>
          <div className="stat-card__value">142</div>
          <div className="stat-card__label">On-Chain Anchors</div>
        </div>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Event</th>
              <th>Bank</th>
              <th>Round</th>
              <th>Attack Type</th>
              <th>Anomaly Score</th>
              <th>Detection</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {MOCK_EVENTS.map((e) => (
              <tr key={e.id}>
                <td style={{ fontFamily: 'var(--font-mono)' }}>{e.id}</td>
                <td style={{ fontWeight: 500 }}>{e.bank}</td>
                <td>#{e.round}</td>
                <td><span className="badge badge--warning">{e.type}</span></td>
                <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-danger)' }}>{e.score.toFixed(2)}</td>
                <td style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)' }}>{e.method}</td>
                <td>
                  <span className={`badge ${e.resolved ? 'badge--success' : 'badge--danger'}`}>
                    {e.resolved ? 'resolved' : 'active'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
