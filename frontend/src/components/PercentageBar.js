import React from 'react'

export default function PercentageBar({ ai, human }) {
  const aiNum = Number.isFinite(ai) ? ai : 0
  const humanNum = Number.isFinite(human) ? human : 0
  const aiPct = Math.round(aiNum * 100)
  const humanPct = 100 - aiPct
  return (
    <div style={{ border: '1px solid #ccc', borderRadius: 6, overflow: 'hidden', width: '100%', height: 24 }}>
      <div style={{ display: 'flex', width: '100%', height: '100%' }}>
        <div style={{ width: `${humanPct}%`, background: '#4caf50', color: '#fff', textAlign: 'center', fontSize: 12 }}>
          Human {humanPct}%
        </div>
        <div style={{ width: `${aiPct}%`, background: '#1976d2', color: '#fff', textAlign: 'center', fontSize: 12 }}>
          AI {aiPct}%
        </div>
      </div>
    </div>
  )
}
