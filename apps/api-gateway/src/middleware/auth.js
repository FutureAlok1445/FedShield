export default async function authMiddleware(app) {
  app.decorate('authenticate', async (request, reply) => {
    const authHeader = request.headers.authorization
    if (!authHeader) {
      return reply.code(401).send({ error: 'Authorization header is required' })
    }

    try {
      const decoded = await request.jwtVerify()
      const bankId = decoded.bank_id

      if (!bankId) {
        return reply.code(403).send({ error: 'bank_id claim missing in token' })
      }

      const bankStatus = await app.db.getBankStatus(bankId)
      if (bankStatus === 'suspended') {
        return reply.code(403).send({ error: 'Bank is suspended' })
      }

      request.bank = { bank_id: bankId, status: bankStatus }
    } catch (error) {
      return reply.code(401).send({ error: 'Unauthorized' })
    }
  })
}
