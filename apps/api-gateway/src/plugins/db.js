import pg from 'pg'

const { Pool } = pg

export default async function dbPlugin(app) {
  let pool = null

  if (process.env.DATABASE_URL) {
    pool = new Pool({ connectionString: process.env.DATABASE_URL })
  }

  app.decorate('db', {
    query: async (sql, params) => {
      if (pool) {
        const result = await pool.query(sql, params)
        return { rows: result.rows }
      }

      return { rows: [] }
    },
    getBankStatus: async (bankId) => {
      if (!pool) {
        // No DB configured — fail-closed in production, allow in dev
        if (process.env.NODE_ENV === 'production') return 'unknown'
        return 'active'
      }

      try {
        const result = await pool.query('SELECT status FROM banks WHERE id = $1 LIMIT 1', [bankId])
        if (!result.rows.length) return 'unknown'
        return result.rows[0].status || 'active'
      } catch (err) {
        // DB query failed — fail-closed
        return 'unknown'
      }
    }
  })

  app.addHook('onClose', async () => {
    if (pool) {
      await pool.end()
    }
  })
}
