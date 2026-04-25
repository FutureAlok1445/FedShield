import NetworkGlobe from '../components/three/NetworkGlobe'

export default function NetworkPage() {
  return (
    <div className="animate-in">
      <div className="page-header">
        <h1>Network Globe</h1>
        <p>Real-time 3D visualization of the federated bank network, trust connections, and data flow.</p>
      </div>
      <div className="card globe-container" style={{ minHeight: '600px' }}>
        <NetworkGlobe />
      </div>
    </div>
  )
}
