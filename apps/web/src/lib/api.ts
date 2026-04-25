const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:3000'

export default async function fetcher<T>(path: string) {
  const response = await fetch(`${API_BASE}${path}`)

  if (!response.ok) {
    throw new Error(`API error ${response.status}`)
  }

  return (await response.json()) as T
}
