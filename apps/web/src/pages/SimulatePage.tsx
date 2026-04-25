export default function SimulatePage() {
  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Simulation</h1>
        <p>Run multi-bank federation simulations with configurable attack scenarios.</p>
      </div>

      <div className="dashboard-grid dashboard-grid--equal">
        <div className="card">
          <h3 style={{ fontWeight: 600, marginBottom: '1rem' }}>Attack Configuration</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)', display: 'block', marginBottom: '0.25rem' }}>Number of Banks</label>
              <input type="number" defaultValue={10} min={2} max={50}
                style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)' }} />
            </div>
            <div>
              <label style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)', display: 'block', marginBottom: '0.25rem' }}>Malicious Banks</label>
              <input type="number" defaultValue={2} min={0} max={10}
                style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)' }} />
            </div>
            <div>
              <label style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)', display: 'block', marginBottom: '0.25rem' }}>Attack Type</label>
              <select style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)' }}>
                <option>Gradient Scaling</option>
                <option>Sign Flip</option>
                <option>Backdoor</option>
                <option>Sybil Attack</option>
              </select>
            </div>
            <div>
              <label style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)', display: 'block', marginBottom: '0.25rem' }}>Rounds</label>
              <input type="number" defaultValue={20} min={5} max={100}
                style={{ width: '100%', padding: '8px 12px', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)' }} />
            </div>
            <button className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }}>▶ Run Simulation</button>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="empty-state">
            <div className="empty-state__icon">🎮</div>
            <div className="empty-state__title">Simulation Results</div>
            <p>Configure and run a simulation to see results here.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
