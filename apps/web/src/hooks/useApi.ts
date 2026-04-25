import { useEffect, useState } from 'react'
import fetcher from '../lib/api'

type ApiState<T> = {
  data: T | null
  error: string | null
  loading: boolean
}

export default function useApi<T>(path: string) {
  const [state, setState] = useState<ApiState<T>>({ data: null, error: null, loading: true })

  useEffect(() => {
    let mounted = true

    fetcher<T>(path)
      .then((data) => {
        if (mounted) setState({ data, error: null, loading: false })
      })
      .catch((error) => {
        if (mounted) setState({ data: null, error: String(error), loading: false })
      })

    return () => {
      mounted = false
    }
  }, [path])

  return state
}
