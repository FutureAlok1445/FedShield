import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'

// Bank node data (lat/lng of major Indian banks)
const BANK_NODES = [
  { id: 'HDFC', lat: 19.076, lng: 72.877, trust: 0.97, status: 'active' as const },
  { id: 'ICICI', lat: 18.52, lng: 73.856, trust: 0.94, status: 'active' as const },
  { id: 'SBI', lat: 28.614, lng: 77.209, trust: 0.96, status: 'active' as const },
  { id: 'Axis', lat: 12.972, lng: 77.594, trust: 0.91, status: 'active' as const },
  { id: 'Kotak', lat: 19.076, lng: 72.877, trust: 0.34, status: 'suspended' as const },
  { id: 'PNB', lat: 28.704, lng: 77.102, trust: 0.88, status: 'active' as const },
  { id: 'BOB', lat: 22.307, lng: 73.181, trust: 0.92, status: 'active' as const },
  { id: 'Canara', lat: 12.914, lng: 74.856, trust: 0.85, status: 'active' as const },
  { id: 'IDBI', lat: 19.076, lng: 72.877, trust: 0.79, status: 'flagged' as const },
  { id: 'UCO', lat: 22.573, lng: 88.364, trust: 0.82, status: 'active' as const },
  { id: 'IndusInd', lat: 19.076, lng: 72.877, trust: 0.9, status: 'active' as const },
  { id: 'Federal', lat: 9.971, lng: 76.269, trust: 0.86, status: 'active' as const },
]

function latLngToVector3(lat: number, lng: number, r: number): THREE.Vector3 {
  const phi = (90 - lat) * (Math.PI / 180)
  const theta = (lng + 180) * (Math.PI / 180)
  return new THREE.Vector3(
    -r * Math.sin(phi) * Math.cos(theta),
     r * Math.cos(phi),
     r * Math.sin(phi) * Math.sin(theta)
  )
}

function getNodeColor(status: string, trust: number): THREE.Color {
  if (status === 'suspended') return new THREE.Color(0xEF4444)
  if (status === 'flagged') return new THREE.Color(0xF59E0B)
  const hue = trust * 120 / 360
  return new THREE.Color().setHSL(hue, 0.7, 0.5)
}

export default function NetworkGlobe() {
  const containerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    // Scene
    const scene = new THREE.Scene()

    // Camera
    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000)
    camera.position.set(0, 0, 7)

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setSize(container.clientWidth, container.clientHeight)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setClearColor(0xF0F4FF, 1)
    container.appendChild(renderer.domElement)

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.05
    controls.minDistance = 4
    controls.maxDistance = 12
    controls.autoRotate = true
    controls.autoRotateSpeed = 0.3

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
    scene.add(ambientLight)
    const directionalLight = new THREE.DirectionalLight(0x4A90E2, 1.2)
    directionalLight.position.set(5, 3, 5)
    scene.add(directionalLight)

    // Globe (solid)
    const globeGeometry = new THREE.SphereGeometry(2, 64, 64)
    const globeMaterial = new THREE.MeshPhongMaterial({
      color: 0xE8F0FE,
      wireframe: false,
      transparent: true,
      opacity: 0.85,
    })
    const globe = new THREE.Mesh(globeGeometry, globeMaterial)
    scene.add(globe)

    // Wireframe overlay
    const wireframeGeometry = new THREE.SphereGeometry(2.01, 32, 32)
    const wireframeMaterial = new THREE.MeshBasicMaterial({
      color: 0x3B82F6,
      wireframe: true,
      transparent: true,
      opacity: 0.12,
    })
    const wireframe = new THREE.Mesh(wireframeGeometry, wireframeMaterial)
    scene.add(wireframe)

    // Bank nodes
    const nodeGeometry = new THREE.SphereGeometry(0.06, 16, 16)
    const nodes: THREE.Mesh[] = []
    BANK_NODES.forEach((bank) => {
      const pos = latLngToVector3(bank.lat, bank.lng, 2.08)
      const color = getNodeColor(bank.status, bank.trust)
      const material = new THREE.MeshPhongMaterial({
        color,
        emissive: color.clone().multiplyScalar(0.3),
      })
      const node = new THREE.Mesh(nodeGeometry, material)
      node.position.copy(pos)
      node.userData = bank
      scene.add(node)
      nodes.push(node)
    })

    // Central aggregation orb
    const orbGeometry = new THREE.SphereGeometry(0.12, 32, 32)
    const orbMaterial = new THREE.MeshPhongMaterial({
      color: 0x3B82F6,
      emissive: 0x1D4ED8,
      transparent: true,
      opacity: 0.9,
    })
    const orb = new THREE.Mesh(orbGeometry, orbMaterial)
    scene.add(orb)

    // Arcs (bank → center)
    const arcGroup = new THREE.Group()
    scene.add(arcGroup)
    nodes.forEach((node) => {
      if (node.userData.status === 'suspended') return
      const from = node.position.clone()
      const to = new THREE.Vector3(0, 0, 0)
      const mid = from.clone().add(to).multiplyScalar(0.5)
      mid.normalize().multiplyScalar(3.0)

      const curve = new THREE.QuadraticBezierCurve3(from, mid, to)
      const points = curve.getPoints(40)
      const geometry = new THREE.BufferGeometry().setFromPoints(points)
      const material = new THREE.LineBasicMaterial({
        color: 0x3B82F6,
        transparent: true,
        opacity: 0.15,
      })
      arcGroup.add(new THREE.Line(geometry, material))
    })

    // Pulse rings
    const rings: { mesh: THREE.Mesh; speed: number; maxScale: number }[] = []
    function createPulseRing(position: THREE.Vector3) {
      const ringGeometry = new THREE.RingGeometry(0.05, 0.08, 32)
      const ringMaterial = new THREE.MeshBasicMaterial({
        color: 0x10B981,
        transparent: true,
        opacity: 0.7,
        side: THREE.DoubleSide,
      })
      const ring = new THREE.Mesh(ringGeometry, ringMaterial)
      ring.position.copy(position)
      ring.lookAt(new THREE.Vector3(0, 0, 0))
      scene.add(ring)
      rings.push({ mesh: ring, speed: 0.02 + Math.random() * 0.02, maxScale: 3 + Math.random() * 2 })
    }

    // Spawn initial rings
    nodes.filter(n => n.userData.status === 'active').forEach((n, i) => {
      setTimeout(() => createPulseRing(n.position.clone()), i * 800)
    })

    // Animation
    let frameId: number
    const clock = new THREE.Clock()

    const animate = () => {
      const elapsed = clock.getElapsedTime()

      globe.rotation.y += 0.001
      wireframe.rotation.y += 0.001
      arcGroup.rotation.y += 0.001

      // Rotate nodes with globe
      nodes.forEach((node) => {
        const bank = node.userData
        const base = latLngToVector3(bank.lat, bank.lng, 2.08)
        const angle = elapsed * 0.001 * Math.PI * 2
        const cos = Math.cos(angle)
        const sin = Math.sin(angle)
        node.position.x = base.x * cos - base.z * sin
        node.position.z = base.x * sin + base.z * cos
        node.position.y = base.y
      })

      // Pulse orb
      const scale = 1 + Math.sin(elapsed * 2) * 0.1
      orb.scale.set(scale, scale, scale)

      // Animate rings
      rings.forEach((ring, i) => {
        const s = ring.mesh.scale.x + ring.speed
        const mat = ring.mesh.material as THREE.MeshBasicMaterial
        if (s >= ring.maxScale) {
          ring.mesh.scale.set(1, 1, 1)
          mat.opacity = 0.7
        } else {
          ring.mesh.scale.set(s, s, s)
          mat.opacity = 0.7 * (1 - s / ring.maxScale)
        }
      })

      controls.update()
      renderer.render(scene, camera)
      frameId = requestAnimationFrame(animate)
    }

    animate()

    // Resize
    const handleResize = () => {
      if (!container) return
      camera.aspect = container.clientWidth / container.clientHeight
      camera.updateProjectionMatrix()
      renderer.setSize(container.clientWidth, container.clientHeight)
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      cancelAnimationFrame(frameId)
      controls.dispose()
      renderer.dispose()
      container.removeChild(renderer.domElement)
    }
  }, [])

  return <div ref={containerRef} style={{ width: '100%', height: '100%', minHeight: 400 }} />
}
