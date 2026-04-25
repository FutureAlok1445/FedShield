import './styles.css'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppShell from './components/layout/AppShell'
import Dashboard from './pages/Dashboard'
import NetworkPage from './pages/NetworkPage'
import RoundsPage from './pages/RoundsPage'
import BanksPage from './pages/BanksPage'
import AlertsPage from './pages/AlertsPage'
import SecurityPage from './pages/SecurityPage'
import AnalyticsPage from './pages/AnalyticsPage'
import ExplainPage from './pages/ExplainPage'
import CompliancePage from './pages/CompliancePage'
import SimulatePage from './pages/SimulatePage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/dashboard" element={<AppShell />}>
          <Route index element={<Dashboard />} />
          <Route path="network" element={<NetworkPage />} />
          <Route path="rounds" element={<RoundsPage />} />
          <Route path="banks" element={<BanksPage />} />
          <Route path="alerts" element={<AlertsPage />} />
          <Route path="security" element={<SecurityPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="explain" element={<ExplainPage />} />
          <Route path="compliance" element={<CompliancePage />} />
          <Route path="simulate" element={<SimulatePage />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
