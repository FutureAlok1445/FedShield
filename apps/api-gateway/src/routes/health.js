export default async function healthRoutes(app) {
  app.get('/v1/health', async () => ({
    status: 'ok',
    model_round: Number(process.env.MODEL_ROUND || 0),
    uptime_ms: Math.round(process.uptime() * 1000)
  }))
}
