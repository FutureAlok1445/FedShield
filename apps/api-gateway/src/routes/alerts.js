export default async function alertRoutes(app) {
  app.get('/v1/alerts/stream', { websocket: true }, async (connection, request) => {
    const requestUrl = request.raw.url || ''
    const queryPart = requestUrl.includes('?') ? requestUrl.split('?')[1] : ''
    const params = new URLSearchParams(queryPart)
    const token = params.get('token')

    if (!token) {
      connection.socket.send(JSON.stringify({ type: 'error', message: 'token query param required' }))
      connection.socket.close()
      return
    }

    try {
      app.jwt.verify(token)
    } catch (error) {
      connection.socket.send(JSON.stringify({ type: 'error', message: 'invalid token' }))
      connection.socket.close()
      return
    }

    connection.socket.send(
      JSON.stringify({
        type: 'connected',
        data: {
          source: 'fedshield-alerts',
          connected_at: new Date().toISOString()
        }
      })
    )

    const heartbeat = setInterval(() => {
      if (connection.socket.readyState === 1) {
        connection.socket.send(JSON.stringify({ type: 'heartbeat', ts: new Date().toISOString() }))
      }
    }, 15000)

    connection.socket.on('close', () => clearInterval(heartbeat))
  })
}
