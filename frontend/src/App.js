import React, { useState } from 'react'
import { detectAI } from './api'
import ResultCard from './components/ResultCard'
import HealthMeta from './components/HealthMeta'
import './styles.css'

export default function App() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const onSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setResult(null)
    if (!text.trim()) {
      setError('Please paste some text.')
      return
    }
    setLoading(true)
    try {
      const r = await detectAI(text)
      setResult(r)
    } catch (err) {
      setError(err?.message || 'Failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 880, margin: '40px auto', padding: 16 }}>
      <h2>Local AI Text Detector</h2>
      <HealthMeta />
      <form onSubmit={onSubmit}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={14}
          style={{ width: '100%', fontFamily: 'monospace', fontSize: 14 }}
          placeholder="Paste your text here..."
        />
        <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
          <button type="submit" disabled={loading}>{loading ? 'Detecting...' : 'Detect'}</button>
          <button type="button" onClick={() => { setText(''); setResult(null); setError(null) }}>Clear</button>
        </div>
      </form>
      {error && <div style={{ color: 'crimson', marginTop: 8 }}>{error}</div>}
      <ResultCard result={result} />
    </div>
  )
}
