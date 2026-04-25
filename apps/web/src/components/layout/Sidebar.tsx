import { NavLink } from 'react-router-dom'

const navItems = [
  { icon: '🏠', label: 'Overview', path: '/dashboard' },
  { icon: '🌐', label: 'Network Globe', path: '/dashboard/network' },
  { icon: '📊', label: 'Federation Rounds', path: '/dashboard/rounds' },
  { icon: '🏦', label: 'Banks', path: '/dashboard/banks' },
  { icon: '🚨', label: 'Fraud Alerts', path: '/dashboard/alerts' },
  { icon: '🛡️', label: 'Security', path: '/dashboard/security' },
  { icon: '📈', label: 'Analytics', path: '/dashboard/analytics' },
  { icon: '🧠', label: 'Explainability', path: '/dashboard/explain' },
  { icon: '📋', label: 'Compliance', path: '/dashboard/compliance' },
  { icon: '🎮', label: 'Simulation', path: '/dashboard/simulate' },
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2L3 7v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5zm0 2.18l7 3.89v5.07c0 4.52-3.12 8.73-7 9.82-3.88-1.09-7-5.3-7-9.82V8.07l7-3.89z"/>
          <path d="M12 7l-4 2.25V13c0 2.48 1.7 4.8 4 5.5 2.3-.7 4-3.02 4-5.5V9.25L12 7z" opacity="0.6"/>
        </svg>
        FedShield
      </div>
      <ul className="sidebar-nav">
        {navItems.map((item) => (
          <li key={item.path}>
            <NavLink
              to={item.path}
              end={item.path === '/dashboard'}
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </aside>
  )
}
