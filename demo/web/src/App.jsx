import { useEffect, useMemo, useState } from 'react'
import AgentPanel from './AgentPanel.jsx'
import Pipeline from './Pipeline.jsx'
import Site from './Site.jsx'
import usePlayback from './usePlayback.js'
import { DAY_STEPS, LAMS, MAX_STEP, MODES, num, sgn, sunSeries, timeLabel, weekday } from './lib.js'

const KPIS = [
  ['N1', 'net value after AI', '€/wk', (v) => sgn(v)],
  ['VORB', 'value over the free rule', '€/wk', (v) => sgn(v)],
  ['VCR', 'share of best saving', '', (v) => num(v)],
  ['S1', 'grid CO2', 'kg/wk', (v) => num(v, 1)],
  ['O1', 'LLM calls per decision', '', (v) => num(v)],
  ['O5', 'AI cost', '€/wk', (v) => num(v)],
]
const VERDICT = { Good: ['good', '✓ Good'], Improvable: ['imp', '↑ Improvable'] }

const q = new URLSearchParams(location.search)
const hashTab = () => (location.hash === '#kpis' ? 'kpis' : 'sim')
const key = (mode, lam) => `${mode}_${lam}`

function useReducedMotion() {
  const [r, setR] = useState(() => matchMedia('(prefers-reduced-motion: reduce)').matches)
  useEffect(() => {
    const m = matchMedia('(prefers-reduced-motion: reduce)')
    const f = () => setR(m.matches)
    m.addEventListener('change', f)
    return () => m.removeEventListener('change', f)
  }, [])
  return r
}

function Header({ tab }) {
  return (
    <header className="header">
      <img src="/logo.avif" alt="Sense Reply" height="36" />
      <nav>
        {[['sim', 'Simulation'], ['kpis', 'KPIs']].map(([id, label]) => (
          <a key={id} href={'#' + id} className={tab === id ? 'on' : ''} aria-current={tab === id ? 'page' : undefined}>{label}</a>
        ))}
      </nav>
      <div className="meta-list muted">
        <span>Replay 5–12 Jan 2026 on run C's sun, load and prices, start SoC 80 %</span>
        <span>Gemini Flash, stand-in for Devstral 2</span>
        <span>Site: Italy (assumed) · CO2 0.356 kg/kWh</span>
      </div>
    </header>
  )
}

function KpiStrip({ kpis, mode, lam }) {
  const ours = kpis.columns[`Ours ${mode} λ=${lam.toFixed(1)}`]
  const pilot = kpis.columns.C
  return (
    <section className="card kpis">
      {KPIS.map(([id, name, unit, f]) => {
        const [cls, text] = VERDICT[ours[id].verdict] || ['', ours[id].verdict]
        return (
          <div className="kpi" key={id}>
            <div className="muted">{id} · {name}</div>
            <div className="kpi-v">
              <span className="mono big">{f(ours[id].value)}</span>
              {unit && <span className="mono muted">{unit}</span>}
            </div>
            <div className="kpi-foot">
              <span className="mono muted small">pilot C {f(pilot[id].value).replace(/^\+/, '')}</span>
              <span className={'tag ' + cls}>{text}</span>
            </div>
          </div>
        )
      })}
    </section>
  )
}

function PlaybackBar({ pb, run, day, mode, lam, setMode, setLam }) {
  return (
    <section className="card bar">
      <button className="play" onClick={pb.toggle} aria-label={pb.playing ? 'Pause' : 'Play'}>
        {pb.playing ? <svg width="18" height="18"><path d="M4 2h3.5v14H4zM10.5 2H14v14h-3.5z" fill="#fff" /></svg>
          : <svg width="18" height="18"><path d="M4 2l11 7-11 7z" fill="#fff" /></svg>}
      </button>
      <span className="mono time">{timeLabel(run.schedule[pb.step].t)}</span>
      <div className="group" role="group" aria-label="Speed">
        {[1, 4, 16].map((s) => (
          <button key={s} className={'chip' + (pb.speed === s ? ' solid' : '')} onClick={() => pb.setSpeed(s)}>{s}×</button>
        ))}
      </div>
      <div className="group" role="group" aria-label="Day">
        {run.days.map((d, i) => {
          const bad = !d.gate.passed || d.used !== 'plan'
          return (
            <button key={d.start} className={'chip' + (i === day ? ' cur' : '')} onClick={() => pb.seek(i * DAY_STEPS)}
              title={bad ? 'Plan blocked by the replay gate' : 'Plan ran'}>
              <i className="dot" style={{ background: bad ? 'var(--alert)' : 'var(--store)' }} />{weekday(d.start)}
            </button>
          )
        })}
      </div>
      <div className="seg" role="group" aria-label="Mode">
        {MODES.map((m) => (
          <button key={m} className={mode === m ? 'on' : ''} onClick={() => setMode(m)}>
            {m === 'conservative' ? 'Conservative' : 'Upside, shadow'}
          </button>
        ))}
      </div>
      <label className="lam">
        <span className="muted">λ €/kg</span>
        <span className="slider">
          <input type="range" min="0" max="2" step="1" value={LAMS.indexOf(lam)} onChange={(e) => setLam(LAMS[e.target.value])} />
          <span className="ticks mono muted"><span>0</span><span>0.10</span><span>0.50</span></span>
        </span>
      </label>
    </section>
  )
}

function Sim({ data }) {
  const [mode, setMode] = useState(MODES.includes(q.get('mode')) ? q.get('mode') : 'conservative')
  const [lam, setLam] = useState(LAMS.includes(+q.get('lambda')) && q.get('lambda') ? +q.get('lambda') : 0.1)
  const stepParam = q.get('step')
  const pb = usePlayback(Math.min(MAX_STEP, Math.max(0, +stepParam || 0)), stepParam === null)
  const reduced = useReducedMotion()
  const run = data.runs[key(mode, lam)]
  const sun = useMemo(() => sunSeries(run.schedule), [run])
  const day = Math.floor(pb.step / DAY_STEPS)
  const d = run.days[day]

  useEffect(() => {
    const onKey = (e) => {
      if (e.target.closest('input, button, summary')) return
      if (e.code === 'Space') { e.preventDefault(); pb.toggle() }
      else if (e.key === 'ArrowLeft') pb.seek(pb.step - 1)
      else if (e.key === 'ArrowRight') pb.seek(pb.step + 1)
    }
    addEventListener('keydown', onKey)
    return () => removeEventListener('keydown', onKey)
  })

  const blocked = !d.gate.passed
  return (
    <main className="sim">
      <KpiStrip kpis={data.kpis} mode={mode} lam={lam} />
      <Site row={run.schedule[pb.step]} step={pb.step} sun={sun[pb.step]} reducedMotion={reduced} />
      <Pipeline active={pb.step % DAY_STEPS < 3 ? 'agent' : null} fail={blocked ? 'validator' : null} />
      <PlaybackBar pb={pb} run={run} day={day} mode={mode} lam={lam} setMode={setMode} setLam={setLam} />
      <AgentPanel run={run} day={day} mode={mode} lam={lam} />
    </main>
  )
}

export default function App() {
  const [tab, setTab] = useState(hashTab())
  const [data, setData] = useState(null)
  const [err, setErr] = useState(null)

  useEffect(() => {
    const f = () => setTab(hashTab())
    addEventListener('hashchange', f)
    return () => removeEventListener('hashchange', f)
  }, [])

  useEffect(() => {
    const get = (u) => fetch(u).then((r) => (r.ok ? r.json() : Promise.reject(new Error(u + ' ' + r.status))))
    const keys = MODES.flatMap((m) => LAMS.map((l) => [m, l]))
    Promise.all([get('/api/kpis'), ...keys.map(([m, l]) => get(`/api/run?mode=${m}&lambda=${l.toFixed(1)}`))])
      .then(([kpis, ...runs]) => setData({ kpis, runs: Object.fromEntries(keys.map(([m, l], i) => [key(m, l), runs[i]])) }))
      .catch(setErr)
  }, [])

  return (
    <>
      <Header tab={tab} />
      {err ? <p className="status">Could not load the replay data: {err.message}</p>
        : !data ? <p className="status muted">Loading the replay</p>
        : tab === 'kpis' ? <p className="status">The KPI conformity table arrives in session 5.</p>
        : <Sim data={data} />}
    </>
  )
}
