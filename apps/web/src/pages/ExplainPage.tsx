export default function ExplainPage() {
  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Explainability — SHAP Analysis</h1>
        <p>Understand why the model flagged transactions with feature-level attribution waterfall charts.</p>
      </div>

      <div className="card" style={{ marginBottom: 'var(--space-6)' }}>
        <h3 style={{ marginBottom: '1rem', fontWeight: 600 }}>Transaction Lookup</h3>
        <div style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
          <input
            type="text"
            placeholder="Enter transaction hash (e.g. TXN-7a3f2)..."
            style={{
              flex: 1,
              padding: '10px 16px',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--text-sm)',
              outline: 'none',
            }}
          />
          <button className="btn btn-primary">Explain</button>
        </div>
      </div>

      <div className="card" style={{ minHeight: 400 }}>
        <h3 style={{ marginBottom: '1rem', fontWeight: 600 }}>SHAP Feature Attribution</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1.5rem' }}>
          {[
            { feature: 'is_new_device', value: '+0.08', width: '60%', positive: true },
            { feature: 'mcc_is_high_risk', value: '+0.05', width: '40%', positive: true },
            { feature: 'txn_count_1h', value: '+0.03', width: '25%', positive: true },
            { feature: 'amount_zscore_30d', value: '−0.02', width: '15%', positive: false },
          ].map((f) => (
            <div key={f.feature} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span style={{ width: 180, fontFamily: 'var(--font-mono)', fontSize: 'var(--text-sm)' }}>{f.feature}</span>
              <div style={{ flex: 1, height: 28, background: 'var(--color-bg-muted)', borderRadius: 'var(--radius-sm)', overflow: 'hidden' }}>
                <div style={{
                  width: f.width,
                  height: '100%',
                  background: f.positive ? 'var(--color-danger)' : 'var(--color-primary-500)',
                  borderRadius: 'var(--radius-sm)',
                  transition: 'width 600ms ease-out',
                  opacity: 0.7,
                }} />
              </div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-sm)', width: 60, textAlign: 'right' }}>{f.value}</span>
            </div>
          ))}
        </div>
        <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--color-bg-subtle)', borderRadius: 'var(--radius-md)', fontSize: 'var(--text-xs)', fontFamily: 'var(--font-mono)', color: 'var(--color-text-muted)' }}>
          Base value: 0.12 → Output: 0.26 (low risk)
        </div>
      </div>
    </div>
  )
}
