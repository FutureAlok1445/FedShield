import { useEffect, useRef, useState } from 'react'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:3000'

export type FraudAlert = {
  txn_ref_hash: string
  fraud_probability: number
  risk_tier: 'low' | 'medium' | 'high' | 'critical'
  decision: 'allow' | 'review' | 'block'
  scored_at: string
}

type WSMessage = {
  type: 'fraud_alert' | 'round_complete' | 'poisoning_detected'
  data: FraudAlert
}

/**
 * WebSocket hook for real-time fraud alert streaming (PRD §14.3).
 * Auto-reconnects on error with exponential backoff.
 */
export default function useAlertStream(token?: string) {
  const [alerts, setAlerts] = useState<FraudAlert[]>([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const retryRef = useRef(0)

  useEffect(() => {
    if (!token) return

    function connect() {
      const ws = new WebSocket(`${WS_URL}/v1/alerts/stream?token=${token}`)
      wsRef.current = ws

      ws.onopen = () => {
        setConnected(true)
        retryRef.current = 0
      }

      ws.onmessage = (event) => {
        try {
          const msg: WSMessage = JSON.parse(event.data)
          if (msg.type === 'fraud_alert') {
            setAlerts((prev) => [msg.data, ...prev].slice(0, 100))
          }
        } catch {
          // Ignore malformed messages
        }
      }

      ws.onclose = () => {
        setConnected(false)
        const delay = Math.min(1000 * 2 ** retryRef.current, 30000)
        retryRef.current++
        setTimeout(connect, delay)
      }

      ws.onerror = () => ws.close()
    }

    connect()
    return () => wsRef.current?.close()
  }, [token])

  return { alerts, connected }
}
