import { useEffect, useRef, useState } from 'react'
import { DAY_STEPS } from './lib.js'

// Plan-day SoC (ours vs pilot C vs static rule) over the grid buy price: two panels on one time axis, never a dual axis.
// compare.json is on run C inputs, the same inputs as every replay run. The readout follows the hover, else the playback step.
const S_H = 92, P_H = 40, TOP = 8, L = 48
const SERIES = [['ours', 'Ours', 'var(--agent)', ''], ['pilot', 'Pilot C', 'var(--ink)', ''], ['rule', 'Static rule', 'var(--mute)', '4 3']]
const pct = (v) => Math.round(v * 100) + ' %'

export default function DayChart({ run, compare, day, step }) {
  const box = useRef(null)
  const [W, setW] = useState(340)
  const [hover, setHover] = useState(null)
  useEffect(() => {
    const ro = new ResizeObserver(([e]) => { if (e.contentRect.width) setW(e.contentRect.width) })
    ro.observe(box.current)
    return () => ro.disconnect()
  }, [])

  const a = day * DAY_STEPS, sl = (s) => s.slice(a, a + DAY_STEPS)
  const rows = sl(run.schedule)
  const d = { ours: rows.map((r) => r.soc), pilot: sl(compare.series['Pilot C'].soc), rule: sl(compare.series['Static rule'].soc) }
  const price = rows.map((r) => r.buy_eur)
  const n = rows.length, R = W - 4
  const x = (i) => L + ((R - L) * i) / (DAY_STEPS - 1)
  const sB = TOP + S_H, pT = sB + 26, pB = pT + P_H
  const ys = (v) => sB - ((v - 0.1) / 0.8) * S_H
  const lo = Math.min(...price), hi = Math.max(...price)
  const yp = (v) => pB - ((v - lo) / (hi - lo || 1)) * P_H
  const line = (s) => s.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)} ${ys(v).toFixed(1)}`).join('')
  const stepPath = price.map((v, i) => `${i ? `H${x(i).toFixed(1)}V` : `M${x(0)} `}${yp(v).toFixed(1)}`).join('') + `H${x(n - 1)}`
  const cur = hover ?? Math.min(n - 1, step - a)
  const move = (e) => {
    const r = e.currentTarget.getBoundingClientRect()
    setHover(Math.max(0, Math.min(n - 1, Math.round(((e.clientX - r.left - L) / (R - L)) * (DAY_STEPS - 1)))))
  }
  const end = n - 1
  const label = `Battery charge over the plan day: ours ends at ${pct(d.ours[end])}, pilot C ${pct(d.pilot[end])}, static rule ${pct(d.rule[end])}. Buy price ${lo.toFixed(2)} to ${hi.toFixed(2)} €/kWh.`

  return (
    <div className="daychart" ref={box}>
      <div className="dc-leg">
        <span className="mono dc-t">{rows[Math.max(0, cur)].t.slice(11, 16)}</span>
        {SERIES.map(([k, name, c, dash]) => (
          <span key={k}><svg width="16" height="4"><line x1="0" x2="16" y1="2" y2="2" stroke={c} strokeWidth="2" strokeDasharray={dash} /></svg>{name} <b className="mono">{pct(d[k][cur])}</b></span>
        ))}
      </div>
      <svg width={W} height={pB + 20} role="img" aria-label={label} onPointerMove={move} onPointerLeave={() => setHover(null)}>
        {[0, 24, 48, 72].map((i) => (
          <g key={i}>
            <line x1={x(i)} x2={x(i)} y1={TOP} y2={pB} className="dc-grid" />
            <text x={x(i)} y={pB + 16} textAnchor="middle">{rows[i]?.t.slice(11, 16)}</text>
          </g>
        ))}
        <text x={L - 6} y={ys(0.9) + 4} textAnchor="end">90 %</text>
        <text x={L - 6} y={ys(0.1) + 4} textAnchor="end">10 %</text>
        <line x1={L} x2={R} y1={ys(0.1)} y2={ys(0.1)} className="dc-base" />
        {[...SERIES].reverse().map(([k, , c, dash]) => <path key={k} d={line(d[k])} fill="none" stroke={c} strokeWidth="2" strokeDasharray={dash} />)}
        <text x={L} y={pT - 7}>Grid buy price €/kWh <tspan className="dc-val">{price[cur].toFixed(3)}</tspan></text>
        <text x={L - 6} y={pT + 9} textAnchor="end">{hi.toFixed(2)}</text>
        <text x={L - 6} y={pB} textAnchor="end">{lo.toFixed(2)}</text>
        <path d={stepPath} fill="none" stroke="var(--grid)" strokeWidth="1.5" />
        {cur >= 0 && <>
          <line x1={x(cur)} x2={x(cur)} y1={TOP} y2={pB} className="dc-cur" />
          <circle cx={x(cur)} cy={ys(d.ours[cur])} r="4" fill="var(--agent)" stroke="#fff" strokeWidth="2" />
        </>}
      </svg>
    </div>
  )
}
