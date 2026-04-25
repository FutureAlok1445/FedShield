import Fastify from 'fastify'
import fastifyJwt from '@fastify/jwt'
import fastifyCors from '@fastify/cors'
import fastifyHelmet from '@fastify/helmet'
import fastifyRateLimit from '@fastify/rate-limit'
import fastifyWebsocket from '@fastify/websocket'
import fastifySwagger from '@fastify/swagger'
import fastifyRedis from '@fastify/redis'
import healthRoutes from './routes/health.js'
import scoreRoutes from './routes/score.js'
import alertRoutes from './routes/alerts.js'
import authMiddleware from './middleware/auth.js'
import dbPlugin from './plugins/db.js'

const app = Fastify({ logger: true })

app.register(fastifyHelmet)
app.register(fastifyCors, {
  origin: [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    process.env.FRONTEND_URL,
  ].filter(Boolean),
  credentials: true,
})
app.register(fastifyRateLimit, { max: 1000, timeWindow: '1 second' })
const JWT_SECRET = process.env.JWT_SECRET
if (!JWT_SECRET) {
  app.log.warn('JWT_SECRET not set — using insecure fallback. Set JWT_SECRET in production!')
}
app.register(fastifyJwt, { secret: JWT_SECRET || 'dev-only-insecure-fallback-secret' })
if (process.env.REDIS_URL) {
  app.register(fastifyRedis, { url: process.env.REDIS_URL })
} else {
  app.log.warn('REDIS_URL not set. Redis-dependent features will run in local fallback mode.')
}
app.register(fastifyWebsocket)
app.register(dbPlugin)
app.register(authMiddleware)
app.register(fastifySwagger, {
  openapi: {
    info: {
      title: 'FedShield API Gateway',
      version: '0.1.0'
    }
  }
})
app.register(healthRoutes)
app.register(scoreRoutes)
app.register(alertRoutes)

const start = async () => {
  try {
    const port = parseInt(process.env.PORT || '3000', 10)
    await app.listen({ port, host: '0.0.0.0' })
    app.log.info(`API Gateway running on http://0.0.0.0:${port}`)
  } catch (error) {
    app.log.error(error)
    process.exit(1)
  }
}

start()
