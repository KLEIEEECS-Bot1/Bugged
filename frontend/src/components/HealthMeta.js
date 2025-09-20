import React, { useEffect, useState } from 'react'
import { getHealth, getMeta } from '../api'

export default function HealthMeta() {
  const [health, setHealth] = useState('checking...')
  const [meta, setMeta] = useState(null)
  const [err, setErr] = useState(null)

  useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        const h = await getHealth()
        if (mounted) setHealth(h.ok ? 'ok' : 'not ok')
        const m = await getMeta()
        if (mounted) setMeta(m)
      } catch (e) {
        if (mounted) setErr(e.message || 'failed')
      }
    })()
    return () => { mounted = false }
  }, [])

  return (
    <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>
      Health: {health}
      {err && <span style={{ marginLeft: 8, color: 'crimson' }}>Error: {err}</span>}
      {meta && (
        <span style={{ marginLeft: 8 }}>
          Models: {meta.models?.distil} | {meta.models?.roberta} | Offline: {String(meta.offline)}
        </span>
      )}
    </div>
  )
}
