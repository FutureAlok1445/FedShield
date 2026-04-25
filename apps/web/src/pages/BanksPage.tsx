const MOCK_BANKS = [
  { id: 'B001', name: 'HDFC Bank', country: 'IN', tier: 'anchor', status: 'active', trust: 0.97 },
  { id: 'B002', name: 'ICICI Bank', country: 'IN', tier: 'premium', status: 'active', trust: 0.94 },
  { id: 'B003', name: 'State Bank of India', country: 'IN', tier: 'anchor', status: 'active', trust: 0.96 },
  { id: 'B004', name: 'Axis Bank', country: 'IN', tier: 'standard', status: 'active', trust: 0.91 },
  { id: 'B005', name: 'Kotak Bank', country: 'IN', tier: 'standard', status: 'suspended', trust: 0.34 },
]

export default function BanksPage() {
  return (
    <div className="animate-in">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Banks</h1>
          <p>Registered banks in the FedShield federated network.</p>
        </div>
        <button className="btn btn-primary">+ Register Bank</button>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Bank ID</th>
              <th>Name</th>
              <th>Country</th>
              <th>Tier</th>
              <th>Status</th>
              <th>Trust Score</th>
            </tr>
          </thead>
          <tbody>
            {MOCK_BANKS.map((b) => (
              <tr key={b.id}>
                <td style={{ fontFamily: 'var(--font-mono)' }}>{b.id}</td>
                <td style={{ fontWeight: 500 }}>{b.name}</td>
                <td>{b.country}</td>
                <td><span className="badge badge--info">{b.tier}</span></td>
                <td>
                  <span className={`badge ${b.status === 'active' ? 'badge--success' : 'badge--danger'}`}>
                    {b.status}
                  </span>
                </td>
                <td style={{ fontFamily: 'var(--font-mono)' }}>{b.trust.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
