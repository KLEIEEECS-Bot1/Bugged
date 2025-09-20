import React from 'react'
import PercentageBar from './PercentageBar'

const fmt = (v) => (typeof v === 'number' && !Number.isNaN(v) ? v.toFixed(3) : 'n/a')

export default function ResultCard({ result }) {
  if (!result) return null

  const ai = typeof result.proba_ai === 'number' ? result.proba_ai : 0
  const human = typeof result.proba_human === 'number' ? result.proba_human : 0

  const votes = result.votes || {}
  const roberta = votes.roberta
  const mlm_gap = votes.mlm_gap
  const compress = votes.compress
  const borderline = !!votes.borderline

  return (
    <div style={{ marginTop: 16, border: '1px solid #ddd', borderRadius: 8, padding: 16 }}>
      <PercentageBar ai={ai} human={human} />
      <div style={{ marginTop: 8 }}>
        Decision: <strong>{String(result.decision || '').toUpperCase() || 'UNKNOWN'}</strong>
        {borderline && <span style={{ marginLeft: 8, color: '#f57c00' }}>Borderline</span>}
      </div>
      <div style={{ marginTop: 8, fontSize: 12, color: '#555' }}>
        RoBERTa: {fmt(roberta)} | MLM gap: {fmt(mlm_gap)} | Compression: {fmt(compress)} | Latency: {Number.isFinite(result.latency_ms) ? result.latency_ms : 'n/a'} ms
      </div>
    </div>
  )
}
