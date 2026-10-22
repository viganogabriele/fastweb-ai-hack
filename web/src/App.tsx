import { useEffect, useState } from 'react'

type Health = {
  status: string
  version: string
  llm_mode: string
  fastweb_key_configured: boolean
  sources_present: boolean
}

// Placeholder shell (PLT-01). WEB-01 replaces it with the real layout, run selector and badges.
export default function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/health')
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setHealth)
      .catch((e: Error) => setError(e.message))
  }, [])

  return (
    <main style={{ maxWidth: 720, margin: '3rem auto', padding: '0 1rem' }}>
      <h1>Tessera</h1>
      <p>From store signals to decisions.</p>
      {error && <p style={{ color: '#b00020' }}>Backend unreachable: {error}</p>}
      {health && <pre>{JSON.stringify(health, null, 2)}</pre>}
    </main>
  )
}
