import { useEffect, useState } from 'react'
import { num } from './lib.js'

const COLS = [['A', 'A · cost agent'], ['C', 'C · dual agent'], ['Static rule', 'Static rule'], ['S5 conservative', 'S5 conservative'], ['S5 upside', 'S5 upside']]
// Headline rows (mock-kpi); the rest of the workbook's KPIs sit behind "Show all".
const HEAD = ['S_net', 'VCR', 'VORB', 'N1', 'N2', 'O5', 'S2b', 'MAC', 'S1', 'SCR', 'SSR', 'PSR', 'G1', 'B4', 'C5', 'O1']
const VD = { Good: ['g', '✓', 'Good'], Improvable: ['i', '↑', 'Improvable'] }

function fmt(v, unit) {
  if (v === null || v === undefined) return 'n/a'
  const n = unit === 'count' ? 0 : unit.startsWith('kg') || unit.startsWith('g/') || unit.startsWith('kWh') ? 1 : Math.abs(v) >= 0.001 && Math.abs(v) < 0.1 ? 3 : 2
  return num(v, n)
}

function Cell({ c, unit, ours }) {
  const [cls, icon, word] = VD[c.verdict] || []
  return (
    <td className={'n' + (ours ? ' ours' : '')}>
      {fmt(c.value, unit)}
      <span className={'vd ' + (cls || 'none')} title={word} aria-label={word} aria-hidden={!word}>{icon || '✓'}</span>
    </td>
  )
}

function Table({ kpis, ours, label }) {
  const [all, setAll] = useState(false)
  const ids = Object.keys(kpis.meta).filter((id) => all || HEAD.includes(id))
  const groups = [...new Set(ids.map((id) => kpis.meta[id].group))]
  const cols = [...COLS, [ours, label]]
  return (
    <section className="card kt">
      <div className="kt-head">
        <h1>KPI conformity, pilots vs final</h1>
        <span className="muted small"><span className="vd g">✓</span> good <span className="vd i">↑</span> improvable · pilot and S5 columns from the KPI Conformity workbook, Ours from this replay</span>
      </div>
      <div className="kt-scroll">
        <table>
          <thead>
            <tr><th>KPI</th><th>Unit</th><th className="n">Threshold</th>
              {cols.map(([k, label]) => <th key={k} className={'n' + (k === ours ? ' ours' : '')}>{label}</th>)}</tr>
          </thead>
          <tbody>
            {groups.flatMap((g) => [
              <tr className="grp" key={g}><td colSpan={cols.length + 3}>{g}</td></tr>,
              ...ids.filter((id) => kpis.meta[id].group === g).map((id) => {
                const { name, unit } = kpis.meta[id]
                const { direction: d, threshold: t } = kpis.thresholds[id]
                return (
                  <tr key={id}>
                    <td><span className="mono kid">{id}</span>{name}</td>
                    <td className="muted">{unit}</td>
                    <td className="n muted">{d === 0 ? 'context' : `${d > 0 ? '≥' : '≤'} ${t}`}</td>
                    {cols.map(([k]) => <Cell key={k} c={kpis.columns[k][id]} unit={unit} ours={k === ours} />)}
                  </tr>
                )
              }),
            ])}
          </tbody>
        </table>
      </div>
      <button className="btn kt-more" onClick={() => setAll(!all)} aria-expanded={all}>
        {all ? 'Show headline KPIs only' : `Show all ${Object.keys(kpis.meta).length} KPIs`}
      </button>
    </section>
  )
}

function Counts({ kpis, ours, label }) {
  const rows = [...COLS, [ours, label]]
  return (
    <div className="card side">
      <h2>Good KPIs out of those assessed</h2>
      {rows.map(([k, label]) => {
        const vs = Object.values(kpis.columns[k]).map((c) => c.verdict)
        const good = vs.filter((v) => v === 'Good').length
        const n = good + vs.filter((v) => v === 'Improvable').length
        return (
          <div className="cnt" key={k}>
            <span>{label}</span>
            <div className="bar-bg"><div className={k === ours ? 'ours' : k.startsWith('S5') ? 's5' : k === 'Static rule' ? 'rule' : ''} style={{ width: `${n ? (good / n) * 100 : 0}%` }} /></div>
            <span className="mono">{good}/{n}</span>
          </div>
        )
      })}
    </div>
  )
}

function Carbon() {
  const [c, setC] = useState(null)
  useEffect(() => {
    fetch('/api/live/carbon').then((r) => (r.ok ? r.json() : Promise.reject())).then(setC)
      .catch(() => setC({ source: 'constant-0.356', points: [] }))
  }, [])
  if (!c) return <div className="card side"><h2>Italy grid CO2, last 24 h</h2><p className="muted small">Loading ENTSO-E</p></div>
  const pts = c.points
  const live = pts.length > 0
  const gs = [356, ...pts.map((p) => p.g_per_kwh)]
  const W = 400, H = 120, lo = Math.min(...gs) - 20, hi = Math.max(...gs) + 20
  const y = (g) => H - 20 - ((g - lo) / (hi - lo)) * (H - 30)
  const x = (i) => 10 + (i * (W - 20)) / Math.max(1, pts.length - 1)
  const last = pts.at(-1)
  return (
    <div className="card side">
      <div className="side-head">
        <h2>Italy grid CO2, last 24 h</h2>
        <span className="muted small">{live ? `ENTSO-E A75, to ${last.hour.slice(11)}:00 Rome` : 'ENTSO-E unavailable'}</span>
      </div>
      <div className="co2-now">
        <span className="mono big">{live ? Math.round(last.g_per_kwh) : 356}</span>
        <span className="mono muted"> g/kWh {live ? 'latest hour' : 'workbook constant'}</span>
      </div>
      {live ? (
        <svg viewBox={`0 0 ${W} ${H}`} className="co2" role="img" aria-label={`Hourly grid carbon intensity, ${Math.round(Math.min(...pts.map((p) => p.g_per_kwh)))} to ${Math.round(Math.max(...pts.map((p) => p.g_per_kwh)))} g/kWh`}>
          <line x1="10" x2={W - 10} y1={y(356)} y2={y(356)} className="ref" />
          <path d={pts.map((p, i) => `${i ? 'L' : 'M'}${x(i)} ${y(p.g_per_kwh)}`).join('')} className="line" />
          <text x="10" y={H - 2}>{pts[0].hour.slice(11)}:00</text>
          <text x={W - 10} y={H - 2} textAnchor="end">{last.hour.slice(11)}:00</text>
        </svg>
      ) : <p className="muted small">No live data (no token or ENTSO-E down). The KPIs use the workbook constant either way.</p>}
      <p className="muted small">{live ? 'Dashed line: workbook constant 356 g/kWh, which the KPIs use.' : ''}</p>
    </div>
  )
}

function Measurable({ run }) {
  const days = run.days
  const rows = [
    ['F5', 'Fallback rate', `${days.filter((d) => d.used !== 'plan').length} / ${days.length} days`],
    ['P4', 'Invalid-output rate', `${days.filter((d) => d.validator_notes.some((n) => n.includes('invalid'))).length} / ${days.length} plans`],
    ['P4', 'Clamp rate', `${days.filter((d) => d.validator_notes.some((n) => n.includes('clamped'))).length} / ${days.length} plans`],
    ['P4', 'Explanation share', `${days.filter((d) => d.explanation?.trim()).length} / ${days.length} plans`],
  ]
  return (
    <div className="card side">
      <h2>Now measurable in the replay</h2>
      <p className="muted small">The pilots logged no proposals, so the workbook marks these "not assessable". The replay logs every plan.</p>
      {rows.map(([id, name, v]) => (
        <div className="row" key={name}><span><span className="mono kid">{id}</span>{name}</span><span className="mono">{v}</span></div>
      ))}
    </div>
  )
}

export default function Kpis({ kpis, run, mode, lam }) {
  const ours = `Ours ${mode} λ=${lam.toFixed(1)}`
  const label = `Ours, ${mode === 'conservative' ? 'conservative' : 'upside'} λ ${lam.toFixed(2)}`
  return (
    <main className="kpitab">
      <Table kpis={kpis} ours={ours} label={label} />
      <aside>
        <Counts kpis={kpis} ours={ours} label={label} />
        <Carbon />
        <Measurable run={run} />
      </aside>
    </main>
  )
}
