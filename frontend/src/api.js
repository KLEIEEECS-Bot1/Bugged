const isDev = !process.env.NODE_ENV || process.env.NODE_ENV === 'development'
const BACKEND_BASE = isDev ? '' : (process.env.REACT_APP_BACKEND_BASE || 'http://wss.rohitmachigad.space:8080')

export async function detectAI(text) {
  const res = await fetch(`${BACKEND_BASE}/detect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  })
  if (!res.ok) {
    const t = await res.text()
    throw new Error(`Detect failed: ${res.status} ${t}`)
  }
  return res.json()
}

export async function getHealth() {
  const res = await fetch(`${BACKEND_BASE}/health`)
  if (!res.ok) throw new Error(`Health failed: ${res.status}`)
  return res.json()
}

export async function getMeta() {
  const res = await fetch(`${BACKEND_BASE}/meta`)
  if (!res.ok) throw new Error(`Meta failed: ${res.status}`)
  return res.json()
}
