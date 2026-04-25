import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import StatCard from '../components/ui/StatCard'
import NetworkGlobe from '../components/three/NetworkGlobe'

const stats = [
  { label: 'Active Banks', value: '47', accent: 'blue', icon: '🏦', sub: '+3 this week', target: 47 },
  { label: 'Federation Rounds', value: '142', accent: 'green', icon: '🔄', sub: 'Round 143 in 2h 14m', target: 142 },
  { label: 'Global AUC', value: '0.9421', accent: 'purple', icon: '📈', sub: '+0.2301 vs isolated avg', target: 0.9421 },
  { label: 'Threats Blocked (24h)', value: '2,847', accent: 'red', icon: '🛡️', sub: '$1.2M protected', target: 2847 },
]

export default function Dashboard() {
  const statsRef = useRef<HTMLDivElement>(null)
  const numbersRef = useRef<(HTMLSpanElement | null)[]>([])

  useEffect(() => {
    // GSAP staggered entrance (PRD §7.2)
    if (statsRef.current) {
      gsap.from(statsRef.current.querySelectorAll('.stat-card'), {
        y: 20,
        opacity: 0,
        duration: 0.5,
        stagger: 0.08,
        ease: 'power2.out',
        clearProps: 'all',
      })
    }

    // GSAP number count-up (PRD §7.2)
    numbersRef.current.forEach((el, i) => {
      if (!el) return
      const stat = stats[i]
      const decimals = stat.target < 10 ? 4 : 0
      gsap.from({ val: 0 }, {
        val: stat.target,
        duration: 1.5,
        ease: 'power2.out',
        onUpdate: function () {
          const v = this.targets()[0].val
          el.textContent = decimals > 0 ? v.toFixed(decimals) : Math.round(v).toLocaleString()
        },
      })
    })
  }, [])

  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Federation Overview</h1>
        <p>Real-time federated fraud intelligence — FLTrust defense active.</p>
      </div>

      <div className="stat-grid" ref={statsRef}>
        {stats.map((s, i) => (
          <StatCard
            key={s.label}
            label={s.label}
            value={s.value}
            accent={s.accent}
            icon={s.icon}
            sub={s.sub}
            valueRef={(el: HTMLSpanElement | null) => { numbersRef.current[i] = el }}
          />
        ))}
      </div>

      <div className="dashboard-grid dashboard-grid--2col">
        <div className="card globe-container" style={{ minHeight: 420, padding: 0, overflow: 'hidden' }}>
          <NetworkGlobe />
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', fontWeight: 600 }}>Federation Health</h3>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', lineHeight: 1.7 }}>
            The FedShield aggregation server uses <strong>FLTrust Byzantine-robust scoring</strong>,
            3-layer gradient anomaly detection, and <strong>on-chain audit anchoring</strong> to protect
            banks from poisoned model updates.
          </p>
          <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-sm)' }}>
              <span style={{ color: 'var(--color-text-muted)' }}>Global model status</span>
              <span className="badge badge--success">Round 142 Active</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-sm)' }}>
              <span style={{ color: 'var(--color-text-muted)' }}>Last aggregation</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>14 min ago</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-sm)' }}>
              <span style={{ color: 'var(--color-text-muted)' }}>Blockchain anchors</span>
              <span className="badge badge--success">142 verified</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-sm)' }}>
              <span style={{ color: 'var(--color-text-muted)' }}>Poisoning events (30d)</span>
              <span className="badge badge--danger">7 detected</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-sm)' }}>
              <span style={{ color: 'var(--color-text-muted)' }}>AUC improvement</span>
              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-success)', fontWeight: 600 }}>+0.23</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
