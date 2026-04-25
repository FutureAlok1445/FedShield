type StatCardProps = {
  label: string
  value: string
  accent: string
  icon: string
  sub?: string
  valueRef?: (el: HTMLSpanElement | null) => void
}

export default function StatCard({ label, value, accent, icon, sub, valueRef }: StatCardProps) {
  return (
    <div className={`stat-card stat-card--${accent}`}>
      <div className="stat-card__icon">{icon}</div>
      <div className="stat-card__value">
        <span ref={valueRef}>{value}</span>
      </div>
      <div className="stat-card__label">{label}</div>
      {sub && <div className="stat-card__sub">{sub}</div>}
    </div>
  )
}
