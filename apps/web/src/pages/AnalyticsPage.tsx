import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

// Mock Data for the Analytics
const aucTrendData = [
  { round: 'Rd 35', auc: 0.88, baseline: 0.82 },
  { round: 'Rd 36', auc: 0.89, baseline: 0.82 },
  { round: 'Rd 37', auc: 0.89, baseline: 0.83 },
  { round: 'Rd 38', auc: 0.91, baseline: 0.83 },
  { round: 'Rd 39', auc: 0.92, baseline: 0.84 },
  { round: 'Rd 40', auc: 0.94, baseline: 0.84 },
  { round: 'Rd 41', auc: 0.95, baseline: 0.85 },
  { round: 'Rd 42', auc: 0.96, baseline: 0.85 },
]

const bankContributionData = [
  { name: 'Global Bank', gradients: 42, trust: 0.98 },
  { name: 'EuroTrust', gradients: 39, trust: 0.95 },
  { name: 'AsiaPay', gradients: 35, trust: 0.91 },
  { name: 'NeoBank X', gradients: 12, trust: 0.45 }, // Malicious flag
  { name: 'CryptoFin', gradients: 8, trust: 0.12 },
]

const riskDistributionData = [
  { name: 'Low Risk', value: 85000, color: '#10b981' }, // emerald-500
  { name: 'Medium Risk', value: 12000, color: '#f59e0b' }, // amber-500
  { name: 'High Risk', value: 2500, color: '#ef4444' }, // red-500
  { name: 'Critical (Blocked)', value: 500, color: '#7f1d1d' }, // red-900
]

const latencyData = [
  { time: '00:00', p95: 12, p99: 18 },
  { time: '04:00', p95: 10, p99: 15 },
  { time: '08:00', p95: 14, p99: 22 },
  { time: '12:00', p95: 18, p99: 28 }, // Peak load
  { time: '16:00', p95: 16, p99: 25 },
  { time: '20:00', p95: 11, p99: 16 },
]

// Custom Tooltip Styles for Dark Mode
const customTooltipStyle = {
  backgroundColor: '#1e293b', // slate-800
  border: '1px solid #334155', // slate-700
  borderRadius: '8px',
  color: '#f8fafc',
}

export default function AnalyticsPage() {
  return (
    <div className="animate-in" style={{ paddingBottom: 'var(--space-8)' }}>
      <div className="page-header">
        <h1>Analytics & Telemetry</h1>
        <p>Real-time federated model performance, bank contribution trust metrics, and latency SLA monitoring.</p>
      </div>

      <div className="dashboard-grid dashboard-grid--equal">
        <div className="card">
          <h3 style={{ marginBottom: 'var(--space-4)', fontSize: '1rem', color: 'var(--text-secondary)' }}>
            Model Performance (AUC Trend)
          </h3>
          <div style={{ height: 300, width: '100%' }}>
            <ResponsiveContainer>
              <LineChart data={aucTrendData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="round" stroke="#94a3b8" fontSize={12} tickLine={false} />
                <YAxis domain={[0.7, 1.0]} stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={customTooltipStyle} itemStyle={{ color: '#e2e8f0' }} />
                <Legend verticalAlign="top" height={36} iconType="circle" />
                <Line
                  type="monotone"
                  dataKey="auc"
                  name="Global Model AUC"
                  stroke="#3b82f6" // blue-500
                  strokeWidth={3}
                  dot={{ r: 4, fill: '#3b82f6', strokeWidth: 0 }}
                  activeDot={{ r: 6 }}
                />
                <Line
                  type="monotone"
                  dataKey="baseline"
                  name="Isolated Baseline"
                  stroke="#64748b" // slate-500
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 'var(--space-4)', fontSize: '1rem', color: 'var(--text-secondary)' }}>
            Bank Contribution & FLTrust Scores
          </h3>
          <div style={{ height: 300, width: '100%' }}>
            <ResponsiveContainer>
              <BarChart data={bankContributionData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={customTooltipStyle} cursor={{ fill: '#334155', opacity: 0.4 }} />
                <Legend verticalAlign="top" height={36} iconType="circle" />
                <Bar dataKey="gradients" name="Submissions (Rounds)" fill="#6366f1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="trust" name="Avg Trust Score (x100)" fill="#10b981" radius={[4, 4, 0, 0]}>
                  {bankContributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.trust > 0.8 ? '#10b981' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="dashboard-grid dashboard-grid--equal" style={{ marginTop: 'var(--space-6)' }}>
        <div className="card">
          <h3 style={{ marginBottom: 'var(--space-4)', fontSize: '1rem', color: 'var(--text-secondary)' }}>
            Scored Transaction Risk Distribution (24h)
          </h3>
          <div style={{ height: 300, width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ResponsiveContainer>
              <PieChart>
                <Tooltip contentStyle={customTooltipStyle} itemStyle={{ color: '#e2e8f0' }} />
                <Legend verticalAlign="bottom" height={36} iconType="circle" />
                <Pie
                  data={riskDistributionData}
                  cx="50%"
                  cy="45%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {riskDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 'var(--space-4)', fontSize: '1rem', color: 'var(--text-secondary)' }}>
            Inference Latency SLA (API Gateway)
          </h3>
          <div style={{ height: 300, width: '100%' }}>
            <ResponsiveContainer>
              <AreaChart data={latencyData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorP99" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorP95" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} unit="ms" />
                <Tooltip contentStyle={customTooltipStyle} />
                <Legend verticalAlign="top" height={36} iconType="circle" />
                <Area
                  type="monotone"
                  dataKey="p99"
                  name="p99 Latency (ms)"
                  stroke="#ef4444"
                  fillOpacity={1}
                  fill="url(#colorP99)"
                />
                <Area
                  type="monotone"
                  dataKey="p95"
                  name="p95 Latency (ms)"
                  stroke="#10b981"
                  fillOpacity={1}
                  fill="url(#colorP95)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
