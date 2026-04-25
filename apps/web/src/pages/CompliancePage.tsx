const REPORT_TYPES = [
  { id: 'rbi_dpsp', name: 'RBI DPSP', desc: 'Reserve Bank of India — Digital Payment Security Procedures' },
  { id: 'gdpr_art30', name: 'GDPR Art. 30', desc: 'EU General Data Protection Regulation — Records of Processing' },
  { id: 'pci_dss', name: 'PCI-DSS', desc: 'Payment Card Industry Data Security Standard' },
  { id: 'fiu_ind', name: 'FIU-IND', desc: 'Financial Intelligence Unit — India' },
]

export default function CompliancePage() {
  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Compliance</h1>
        <p>Generate and download regulatory compliance reports for your institution.</p>
      </div>

      <div className="stat-grid">
        {REPORT_TYPES.map((rt) => (
          <div className="card" key={rt.id} style={{ cursor: 'pointer' }}>
            <h3 style={{ fontWeight: 600, marginBottom: '0.5rem' }}>{rt.name}</h3>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', marginBottom: '1rem', lineHeight: 1.6 }}>
              {rt.desc}
            </p>
            <button className="btn btn-secondary" style={{ width: '100%' }}>Generate Report</button>
          </div>
        ))}
      </div>
    </div>
  )
}
