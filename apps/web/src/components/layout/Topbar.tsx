import { useLocation } from 'react-router-dom'

const pageTitles: Record<string, string> = {
  '/dashboard': 'Overview',
  '/dashboard/network': 'Network Globe',
  '/dashboard/rounds': 'Federation Rounds',
  '/dashboard/banks': 'Banks',
  '/dashboard/alerts': 'Fraud Alerts',
  '/dashboard/security': 'Security',
  '/dashboard/analytics': 'Analytics',
  '/dashboard/explain': 'Explainability',
  '/dashboard/compliance': 'Compliance',
  '/dashboard/simulate': 'Simulation',
}

export default function Topbar() {
  const location = useLocation()
  const title = pageTitles[location.pathname] || 'FedShield'

  return (
    <header className="topbar">
      <h2 className="topbar-title">{title}</h2>
      <div className="topbar-actions">
        <span className="status-pill status-pill--active">
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'currentColor' }} />
          Round Active
        </span>
        <span style={{ fontSize: '1.25rem', cursor: 'pointer' }}>🔔</span>
      </div>
    </header>
  )
}
