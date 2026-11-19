import DayChart from './DayChart.jsx'
import { dayLabel, eur, kfmt, nextDayWeekday, parts } from './lib.js'

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b)

function Knob({ label, unit, used, proposed, show }) {
  const changed = proposed !== undefined && !same(used, proposed)
  return (
    <div className="row">
      <span>{label}</span>
      <span className="mono">
        {changed && <s className="muted">{show(proposed)}</s>}{' '}
        {show(used)}{unit && <span className="muted"> {unit}</span>}
      </span>
    </div>
  )
}

export default function AgentPanel({ run, compare, day, step, lam }) {
  const d = run.days[day]
  const blocked = !d.gate.passed
  const prop = blocked ? d.proposed : {}
  const delta = d.gate.score_default - d.gate.score_plan
  const download = () => {
    const a = document.createElement('a')
    a.href = URL.createObjectURL(new Blob([JSON.stringify(run, null, 2)], { type: 'application/json' }))
    a.download = `run_${lam.toFixed(1)}.json`
    a.click()
    setTimeout(() => URL.revokeObjectURL(a.href))
  }
  return (
    <aside className="card panel">
      <h2>Plan for {dayLabel(d.start)}</h2>
      <p className="mono meta">
        decided {parts(d.start).hm} · runs to {nextDayWeekday(d.start)} 10:45<br />1 call ·{' '}
        <span>{kfmt(d.tok_in + d.tok_out)} tokens</span>
      </p>
      <p className="muted small">No grid charging · λ €{lam.toFixed(2)}/kg</p>

      {d.knobs ? <div className="knobs">
        <Knob label="Evening reserve" unit="kWh" used={d.knobs.evening_reserve_kwh} proposed={prop.evening_reserve_kwh} show={(v) => v.toFixed(1)} />
        <Knob label="SoC floor" used={d.knobs.soc_floor} proposed={prop.soc_floor} show={(v) => v.toFixed(2)} />
        <Knob label="Hold export above" unit="€/kWh" used={d.knobs.export_hold_eur} proposed={prop.export_hold_eur} show={(v) => v.toFixed(2)} />
      </div> : <p className="muted small">No valid plan yet this week: the static rule runs the battery today.</p>}

      <p className="why">{blocked && <b>Proposed plan, blocked by the gate: </b>}{d.explanation.replaceAll('**', '')}</p>
      {d.thoughts && <details className="thoughts">
        <summary>Model reasoning</summary>
        <pre>{d.thoughts.replaceAll('**', '')}</pre>
      </details>}

      <h3 className="muted">Checks before the plan runs</h3>
      <ul className="checks">
        <li className={d.validator_notes.length ? 'bad' : ''}>
          <i className="tick">{d.validator_notes.length ? '!' : '✓'}</i>
          <span>{d.validator_notes.length ? d.validator_notes.join('; ') : 'Schema valid'}</span>
        </li>
        <li><i className="tick">✓</i><span>Clamped to SoC 0.1–0.9, 5 kW</span></li>
        <li className={blocked ? 'bad' : ''}>
          <i className="tick">{blocked ? '✕' : '✓'}</i>
          <span>{blocked ? `Blocked, ${d.used} used` : 'Replay gate vs default knobs'}</span>
          <span className="mono muted" title={`Default-knob score minus plan score, € + λ·kg replayed on ${d.gate.basis} (positive: the plan is better)`}>
            {delta < 0 ? '−' : '+'}€{Math.abs(delta).toFixed(3)}
          </span>
        </li>
      </ul>

      <h3 className="muted">Battery charge over this plan day</h3>
      <DayChart run={run} compare={compare} day={day} step={step} />

      <h3 className="muted">Similar past days it was shown</h3>
      <ul className="mem">
        {d.neighbours.map((n) => (
          <li key={n.label}><span>{n.label}</span><span className="mono muted">regret {eur(n.regret, 3)}</span></li>
        ))}
      </ul>
      <p className="muted small">regret vs rule, scored at λ 0.10</p>

      <button className="btn" onClick={download}>Download plan JSON</button>
    </aside>
  )
}
