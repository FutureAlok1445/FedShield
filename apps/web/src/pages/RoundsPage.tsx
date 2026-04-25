const MOCK_ROUNDS = [
  { id: 23, status: 'complete', participants: 12, auc: 0.942, started: '2h ago' },
  { id: 22, status: 'complete', participants: 11, auc: 0.938, started: '6h ago' },
  { id: 21, status: 'complete', participants: 12, auc: 0.935, started: '12h ago' },
  { id: 20, status: 'complete', participants: 10, auc: 0.929, started: '1d ago' },
  { id: 19, status: 'complete', participants: 12, auc: 0.924, started: '2d ago' },
]

export default function RoundsPage() {
  return (
    <div className="animate-in">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Federation Rounds</h1>
          <p>Track aggregation rounds, participants, and model performance over time.</p>
        </div>
        <button className="btn btn-primary">+ Start New Round</button>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Round</th>
              <th>Status</th>
              <th>Participants</th>
              <th>Global AUC</th>
              <th>Started</th>
            </tr>
          </thead>
          <tbody>
            {MOCK_ROUNDS.map((r) => (
              <tr key={r.id}>
                <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>#{r.id}</td>
                <td><span className="badge badge--success">{r.status}</span></td>
                <td>{r.participants}/12</td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>{r.auc.toFixed(3)}</td>
                <td style={{ color: 'var(--color-text-muted)' }}>{r.started}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
